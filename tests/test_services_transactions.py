import pytest
from decimal import Decimal  # <-- Добавьте эту строку
from types import SimpleNamespace
from unittest.mock import AsyncMock

from src.core.exceptions import NotFoundError, AuthorizationError
from src.services.transaction_service import TransactionService

@pytest.mark.asyncio
async def test_transaction_service_get_transaction_not_found():
    session = AsyncMock()
    service = TransactionService(session)

    service.transaction_repo.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(NotFoundError):
        await service.get_transaction(transaction_id=1, user_id=1)


@pytest.mark.asyncio
async def test_transaction_service_delete_transaction_not_found():
    session = AsyncMock()
    service = TransactionService(session)

    service.transaction_repo.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(NotFoundError):
        await service.delete_transaction(transaction_id=1, user_id=1)


@pytest.mark.asyncio
async def test_transaction_service_delete_transaction_forbidden():
    session = AsyncMock()
    service = TransactionService(session)

    # 1. Возвращаем транзакцию, привязанную к аккаунту с ID=99
    tx = SimpleNamespace(id=1, account_id=99, amount=Decimal("100.00"))
    service.transaction_repo.get_by_id = AsyncMock(return_value=tx)

    # 2. Имитируем этот самый аккаунт. 
    # Ставим ему user_id=2 (чтобы он отличался от текущего пользователя, который пытается удалить)
    acc = SimpleNamespace(id=99, user_id=2)
    service.account_repo.get_by_id = AsyncMock(return_value=acc)

    # Пытаемся удалить транзакцию от лица пользователя №1
    with pytest.raises(AuthorizationError):
        await service.delete_transaction(transaction_id=1, user_id=1)

