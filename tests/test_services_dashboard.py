import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

from src.services.dashboard_service import DashboardService

@pytest.mark.asyncio
async def test_dashboard_service_get_dashboard_data():
    session = AsyncMock()
    service = DashboardService(session)

    service.account_repo.get_user_accounts = AsyncMock(return_value=[])
    service.account_repo.get_total_balance = AsyncMock(return_value=Decimal("15000.00"))
    service.transaction_repo.get_total_by_type = AsyncMock(
        side_effect=[Decimal("30000.00"), Decimal("15000.00")]
    )
    service.transaction_repo.get_recent_transactions = AsyncMock(return_value=[])

    result = await service.get_dashboard_data(user_id=1)

    # Используем правильные ключи из Pydantic-схемы (balance и income_expense)
    assert result.balance.total_balance == Decimal("15000.00")
    assert result.income_expense.total_income == Decimal("30000.00")
    assert result.income_expense.total_expense == Decimal("15000.00")
    assert result.recent_transactions == []


@pytest.mark.asyncio
async def test_dashboard_service_default_period():
    session = AsyncMock()
    service = DashboardService(session)

    service.account_repo.get_user_accounts = AsyncMock(return_value=[])
    service.account_repo.get_total_balance = AsyncMock(return_value=Decimal("0.00"))
    service.transaction_repo.get_total_by_type = AsyncMock(
        side_effect=[Decimal("0.00"), Decimal("0.00")]
    )
    service.transaction_repo.get_recent_transactions = AsyncMock(return_value=[])

    result = await service.get_dashboard_data(user_id=1)

    # Используем правильный ключ
    assert result.balance.currency == "RUB"

