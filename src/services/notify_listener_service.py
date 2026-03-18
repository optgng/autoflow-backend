"""
PostgreSQL LISTEN воркер — слушает канал new_finance_transaction.
"""
import asyncio
import json
import logging

import asyncpg
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.config import settings

logger = logging.getLogger(__name__)

# Создаём собственную фабрику сессий для воркера
# (не зависит от FastAPI dependency injection)
_engine = create_async_engine(settings.DATABASE_URL, echo=False)
_session_factory = async_sessionmaker(
    _engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def listen_for_transactions() -> None:
    conn = await asyncpg.connect(
        settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    )
    logger.info("LISTEN new_finance_transaction — воркер запущен")

    async def handle(connection, pid, channel, payload):
        try:
            data        = json.loads(payload)
            telegram_id = data.get("telegram_id")
            if not telegram_id:
                logger.warning("NOTIFY получен без telegram_id")
                return

            logger.info(f"NOTIFY получен: telegram_id={telegram_id}")

            # Импортируем здесь чтобы избежать circular imports
            from src.services.import_service import ImportService

            async with _session_factory() as session:
                service = ImportService(session)
                count   = await service.process_pending(int(telegram_id))
                logger.info(
                    f"Импорт завершён: {count} транзакций для telegram_id={telegram_id}"
                )

        except Exception as e:
            logger.exception(f"Ошибка в handle_notify: {e}")
            # logger.exception — выведет полный traceback, а не только сообщение

    await conn.add_listener("new_finance_transaction", handle)

    try:
        while True:
            await asyncio.sleep(1)
    finally:
        await conn.remove_listener("new_finance_transaction", handle)
        await conn.close()
        await _engine.dispose()

