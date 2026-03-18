"""
Account service.
"""
"""
Account service.
"""
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import AuthorizationError, NotFoundError, ValidationError
from src.repositories.account_repo import AccountRepository
from src.schemas.account import (
    AUTO_IMPORT_TYPES,
    AccountCreate,
    AccountResponse,
    AccountUpdate,
    AccountWithStats,
)


class AccountService:
    """Service for account management."""

    def __init__(self, session: AsyncSession):
        self.session      = session
        self.account_repo = AccountRepository(session)

    # ------------------------------------------------------------------ #
    # Create                                                               #
    # ------------------------------------------------------------------ #

    async def create_account(
        self, user_id: int, data: AccountCreate
    ) -> AccountResponse:
        """Создать счёт (только cash через API)."""
        account = await self.account_repo.create(
            user_id          = user_id,
            name             = data.name,
            account_type     = data.account_type,
            currency         = data.currency,
            balance          = data.balance,
            bank_name        = data.bank_name,
            last_four_digits = data.last_four_digits,
            icon             = data.icon,
            color            = data.color,
            include_in_total = data.include_in_total,
            is_active        = True,
        )
        return AccountResponse.model_validate(account)

    async def create_account_from_import(
        self,
        user_id:          int,
        name:             str,
        account_type:     str,          # "card" | "bank_account"
        currency:         str,
        balance:          Decimal,
        bank_name:        str | None    = None,
        last_four_digits: str | None    = None,
        account_number:   str | None    = None,
    ) -> AccountResponse:
        """
        Создать банковский счёт/карту через ImportService.
        Минует валидатор AccountCreate.only_cash_allowed.
        """
        account = await self.account_repo.create(
            user_id          = user_id,
            name             = name,
            account_type     = account_type,
            currency         = currency,
            balance          = balance,
            bank_name        = bank_name,
            last_four_digits = last_four_digits,
            account_number   = account_number,
            include_in_total = True,
            is_active        = True,
        )
        return AccountResponse.model_validate(account)

    # ------------------------------------------------------------------ #
    # Read                                                                 #
    # ------------------------------------------------------------------ #

    async def get_account(self, account_id: int, user_id: int) -> AccountResponse:
        account = await self.account_repo.get_by_id(account_id)

        if not account:
            raise NotFoundError("Account not found")
        if account.user_id != user_id:
            raise AuthorizationError("Access denied to this account")

        return AccountResponse.model_validate(account)

    async def get_user_accounts(
        self, user_id: int, include_inactive: bool = False
    ) -> list[AccountResponse]:
        accounts = await self.account_repo.get_user_accounts(
            user_id          = user_id,
            include_inactive = include_inactive,
        )
        return [AccountResponse.model_validate(acc) for acc in accounts]

    async def get_accounts_by_type(
        self, user_id: int, account_type: str
    ) -> list[AccountResponse]:
        accounts = await self.account_repo.get_by_type(user_id, account_type)
        return [AccountResponse.model_validate(acc) for acc in accounts]

    async def get_total_balance(
        self, user_id: int, currency: str = "RUB"
    ) -> Decimal:
        return await self.account_repo.get_total_balance(user_id, currency)

    # ------------------------------------------------------------------ #
    # Update                                                               #
    # ------------------------------------------------------------------ #

    async def update_account(
        self, account_id: int, user_id: int, data: AccountUpdate
    ) -> AccountResponse:
        """
        Обновить счёт с проверкой бизнес-правил.

        Правила:
        - cash → нельзя менять тип, нельзя менять bank_name
        - card/bank_account → можно менять тип только card ↔ bank_account
        - нельзя переключить банковский счёт в cash
        """
        account = await self.account_repo.get_by_id(account_id)

        if not account:
            raise NotFoundError("Account not found")
        if account.user_id != user_id:
            raise AuthorizationError("Access denied to this account")

        update_data = data.model_dump(exclude_unset=True)
        if 'balance' in update_data and account.account_type != 'cash':
            del update_data['balance']
        # --- Проверка изменения типа ---
        new_type = update_data.get("account_type")
        if new_type is not None:
            current_type = account.account_type

            if current_type == "cash":
                raise ValidationError(
                    "Нельзя изменить тип счёта наличных. "
                    "Удалите его и дождитесь автоимпорта из выписки."
                )
            if new_type == "cash":
                raise ValidationError(
                    "Нельзя изменить банковский счёт на наличные."
                )
            # Разрешено только card ↔ bank_account — проходит без ошибки

        # --- Запрет bank_name для наличных ---
        if account.account_type == "cash" and "bank_name" in update_data:
            del update_data["bank_name"]

        # --- Страховка: убираем поля, которых нет в AccountUpdate ---
        # (на случай если repo.update принимает **kwargs)
        FORBIDDEN = {"balance", "last_four_digits", "account_number", "user_id"}
        for field in FORBIDDEN:
            update_data.pop(field, None)

        if not update_data:
            return AccountResponse.model_validate(account)

        updated = await self.account_repo.update(account_id, **update_data)
        return AccountResponse.model_validate(updated)

    # ------------------------------------------------------------------ #
    # Delete                                                             #
    # ------------------------------------------------------------------ #

    async def delete_account(self, account_id: int, user_id: int) -> bool:
        """
        Удалить счёт.
        Банковские счета/карты с транзакциями — только деактивация (soft delete).
        Наличные — полное удаление.
        """
        account = await self.account_repo.get_by_id(account_id)

        if not account:
            raise NotFoundError("Account not found")
        if account.user_id != user_id:
            raise AuthorizationError("Access denied to this account")

        if account.account_type in AUTO_IMPORT_TYPES:
            # Мягкое удаление — просто деактивируем
            await self.account_repo.update(account_id, is_active=False)
            return True

        # Для наличных — полное удаление
        return await self.account_repo.delete(account_id)

    # ------------------------------------------------------------------ #
    # Import Service                                                     #
    # ------------------------------------------------------------------ #
    
    async def get_accounts_by_number(
        self, user_id: int, account_number: str
    ) -> AccountResponse | None:
        """Поиск счёта по полному номеру."""
        result = await self.account_repo.get_by_account_number(user_id, account_number)
        return AccountResponse.model_validate(result) if result else None

    async def get_account_by_last4(
        self, user_id: int, last4: str
    ) -> AccountResponse | None:
        """Поиск карты/счёта по последним 4 цифрам."""
        result = await self.account_repo.get_by_last_four(user_id, last4)
        return AccountResponse.model_validate(result) if result else None

    async def update_account_number(
        self, account_id: int, account_number: str
    ) -> None:
        """Обновить полный номер счёта (только для ImportService)."""
        await self.account_repo.update(account_id, account_number=account_number)
