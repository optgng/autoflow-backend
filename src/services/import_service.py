"""
Import Service — обрабатывает транзакции из bot.finance_transactions.
"""
from decimal import Decimal
from datetime import date, datetime, timezone
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.models.user import User
from src.models.transaction import Transaction
from src.schemas.account import AccountResponse
from src.services.account_service import AccountService
from src.services.category_service import CategoryService
from src.services.enrichment_service import enrich_transactions
from src.services.settlement_detector import detect_settlements, extract_contact_ref
from src.config import settings

logger = logging.getLogger(__name__)


class ImportService:

    def __init__(self, session: AsyncSession):
        self.session          = session
        self.account_service  = AccountService(session)
        self.category_service = CategoryService(session)

    # ------------------------------------------------------------------ #
    # Точка входа                                                          #
    # ------------------------------------------------------------------ #

    async def process_pending(self, telegram_id: int) -> int:
        """
        Обрабатывает все pending записи пользователя.
        Возвращает количество импортированных транзакций.
        """
        logger.info(f"process_pending вызван для telegram_id={telegram_id}")
        user = await self._get_user_by_telegram(telegram_id)
        if not user:
            logger.warning(f"Пользователь с telegram_id={telegram_id} не найден")
            return 0

        rows = await self.session.execute(
            text("""
                SELECT id, account_number, date_msk, time_msk,
                       auth_code, category, amount, tx_type,
                       balance, date_operation, merchant
                FROM bot.finance_transactions
                WHERE telegram_id   = :telegram_id
                  AND import_status = 'pending'
                ORDER BY date_msk, time_msk
            """),
            {"telegram_id": telegram_id},
        )
        pending = rows.mappings().all()

        if not pending:
            return 0

        imported = 0
        last_balances: dict[str, Decimal] = {}
        imported_txs = []
        
        for row in pending:
            try:
                tx = await self._process_row(user, dict(row))
                if tx:
                    imported_txs.append(tx)
                await self.session.execute(
                    text("""
                        UPDATE bot.finance_transactions
                        SET import_status = 'done', imported_at = NOW()
                        WHERE id = :id
                    """),
                    {"id": row["id"]},
                )
                imported += 1
                acc_num = row.get("account_number", "")
                if row.get("balance") is not None:
                    last_balances[acc_num] = Decimal(str(row.get("balance", 0)))
            except Exception as e:
                logger.error(f"Ошибка импорта строки id={row['id']}: {e}")
                await self.session.execute(
                    text("UPDATE bot.finance_transactions SET import_status = 'error' WHERE id = :id"),
                    {"id": row["id"]},
                )

        # Финальное обновление балансов — только ОДИН раз, через raw SQL
        # Минуем ORM-кэш полностью
        for account_number, final_balance in last_balances.items():
            logger.info(f"Updating balance for {account_number}: {final_balance}")
            await self.session.execute(
                text("""
                    UPDATE finances.accounts
                    SET balance = :balance, updated_at = NOW()
                    WHERE account_number = :account_number
                      AND user_id = :user_id
                """),
                {
                    "balance": final_balance,
                    "account_number": account_number,
                    "user_id": user.id,
                },
            )

        await self.session.commit()

        # ── Ensure user_keys salt exists ──────────────────────────
        await self._ensure_user_salt(telegram_id)

        # ── Phase 1: Rule Engine ──────────────────────────────────
        if settings.PIPELINE_RULE_ENGINE and imported_txs:
            if settings.PIPELINE_LOG_VERBOSE:
                logger.info(f"[PIPELINE] Rule engine: {len(imported_txs)} transactions")
            await enrich_transactions(self.session, imported_txs, telegram_id)

        # ── Phase 2: Settlement Detector ─────────────────────────
        if settings.PIPELINE_SETTLEMENT and imported_txs:
            tx_dicts = [
                {"id": tx.id, "merchant": tx.merchant, "txtype": tx.transaction_type,
                 "amount": str(tx.amount), "date": str(tx.transaction_date)}
                for tx in imported_txs
            ]
            from src.services.settlement_detector import detect_settlements
            salt = await self._get_salt_bytes(telegram_id)
            pairs = detect_settlements(tx_dicts, salt)
            if pairs and settings.PIPELINE_LOG_VERBOSE:
                logger.info(f"[PIPELINE] Settlement pairs found: {len(pairs)}")

        logger.info(f"Импортировано {imported} транзакций для telegram_id={telegram_id}")
        return imported
    # ------------------------------------------------------------------ #
    # Обработка одной строки                                               #
    # ------------------------------------------------------------------ #

    async def _process_row(self, user: User, row: dict) -> None:
        if row.get("auth_code"):
            dup = await self.session.execute(
                select(Transaction).where(
                    Transaction.user_id == user.id,
                    Transaction.external_id == row["auth_code"],
                )
            )
            if dup.scalar_one_or_none():
                return None

        account = await self._resolve_account(user, row)
        category = await self._resolve_category(user, row)

        tx_date = row["date_msk"]
        if isinstance(tx_date, str):
            tx_date = date.fromisoformat(tx_date)

        tx = Transaction(
            user_id=user.id,
            account_id=account.id,
            category_id=category.id if category else None,
            transaction_date=tx_date,
            amount=Decimal(str(row["amount"])),
            transaction_type=row["tx_type"],
            merchant=row.get("merchant"),
            external_id=row.get("auth_code"),
            import_source="sber_pdf",
        )
        self.session.add(tx)
        await self.session.flush()
        return tx
    # ------------------------------------------------------------------ #
    # Резолв счёта                                                         #
    # ------------------------------------------------------------------ #

    async def _resolve_account(self, user: User, row: dict) -> AccountResponse:
        """
        Ищет счёт по account_number.
        Если не найден — создаёт через AccountService.create_account_from_import.
        """
        account_number = row.get("account_number", "")
        last4 = account_number[-4:] if len(account_number) >= 4 else account_number

        # Ищем по точному номеру
        existing = await self.account_service.get_accounts_by_number(
            user.id, account_number
        )
        if existing:
            return existing

        # Ищем по последним 4 цифрам среди card/bank_account
        existing_by_last4 = await self.account_service.get_account_by_last4(
            user.id, last4
        )
        if existing_by_last4:
            # Сохраняем полный номер
            await self.account_service.update_account_number(
                existing_by_last4.id, account_number
            )
            return existing_by_last4

        # Создаём новый счёт
        return await self.account_service.create_account_from_import(
            user_id          = user.id,
            name             = f"Сбер ****{last4}",
            account_type     = "card",
            currency         = "RUB",
            balance          = Decimal(0),
            bank_name        = "Сбербанк",
            last_four_digits = last4,
            account_number   = account_number,
        )

    # ------------------------------------------------------------------ #
    # Резолв категории                                                     #
    # ------------------------------------------------------------------ #

    async def _resolve_category(self, user: User, row: dict):
        """
        Ищет категорию по имени среди пользовательских и системных.
        Если не найдена — создаёт автоматически.
        """
        category_name = row.get("category", "").strip()
        if not category_name:
            return None

        # Ищем среди существующих (включая системные)
        all_categories = await self.category_service.get_user_categories(
            user.id, include_system=True
        )
        for cat in all_categories:
            if cat.name.lower() == category_name.lower():
                return cat

        # Автосоздание
        from src.schemas.category import CategoryCreate
        new_cat = await self.category_service.create_category(
            user.id,
            CategoryCreate(
                name          = category_name,
                category_type = row.get("tx_type", "expense"),
            ),
        )
        return new_cat

    # ------------------------------------------------------------------ #
    # Вспомогательное                                                      #
    # ------------------------------------------------------------------ #

    async def _get_user_by_telegram(self, telegram_id: int) -> User | None:
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()


    # ------------------------------------------------------------------ #
    # Соль пользователей                                                 #
    # ------------------------------------------------------------------ #

    async def _ensure_user_salt(self, telegram_id: int) -> None:
        """Создаёт запись user_keys если её нет."""
        from sqlalchemy import text
        import secrets
        existing = await self.session.execute(
            text("SELECT id FROM finances.user_keys WHERE telegram_id = :tid"),
            {"tid": telegram_id},
        )
        if not existing.fetchone():
            salt = secrets.token_hex(32)  # 64-char hex
            await self.session.execute(
                text("INSERT INTO finances.user_keys (telegram_id, salt) VALUES (:tid, :salt)"),
                {"tid": telegram_id, "salt": salt},
            )
            await self.session.commit()
            logger.info(f"[PIPELINE] Created user_key salt for telegram_id={telegram_id}")

    async def _get_salt_bytes(self, telegram_id: int) -> bytes:
        from sqlalchemy import text
        result = await self.session.execute(
            text("SELECT salt FROM finances.user_keys WHERE telegram_id = :tid"),
            {"tid": telegram_id},
        )
        row = result.fetchone()
        if row:
            return bytes.fromhex(row[0]) if isinstance(row[0], str) else row[0]
        return settings.SECRET_KEY.encode()[:32]  # fallback

