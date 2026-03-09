"""
Dashboard service.
"""
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.account_repo import AccountRepository
from src.repositories.transaction_repo import TransactionRepository
from src.schemas.dashboard import (
    BalanceOverview,
    DashboardData,
    IncomeExpenseSummary,
)
from src.schemas.account import AccountResponse
from src.schemas.transaction import TransactionResponse


class DashboardService:
    """Service for dashboard data aggregation."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.account_repo = AccountRepository(session)
        self.transaction_repo = TransactionRepository(session)

    async def get_dashboard_data(
        self,
        user_id: int,
        period_start: date | None = None,
        period_end: date | None = None,
    ) -> DashboardData:
        """
        Get dashboard data for user.
        
        Args:
            user_id: User ID
            period_start: Start date (default: 30 days ago)
            period_end: End date (default: today)
            
        Returns:
            Dashboard data
        """
        # Default period: last 30 days
        if not period_end:
            period_end = date.today()
        
        if not period_start:
            period_start = period_end - timedelta(days=30)
        
        # Get balance overview
        balance = await self._get_balance_overview(user_id)
        
        # Get income/expense summary
        income_expense = await self._get_income_expense_summary(
            user_id, period_start, period_end
        )
        
        # Get top accounts
        accounts = await self.account_repo.get_user_accounts(
            user_id, include_inactive=False, limit=5
        )
        top_accounts = [AccountResponse.model_validate(acc) for acc in accounts]
        
        # Get recent transactions
        transactions = await self.transaction_repo.get_recent_transactions(
            user_id, limit=10
        )
        recent_transactions = [
            TransactionResponse.model_validate(tx) for tx in transactions
        ]
        
        return DashboardData(
            period_start=period_start,
            period_end=period_end,
            balance=balance,
            income_expense=income_expense,
            top_accounts=top_accounts,
            recent_transactions=recent_transactions,
            expense_by_category=[],  # TODO: Implement in analytics service
            income_by_category=[],   # TODO: Implement in analytics service
            monthly_trend=[],         # TODO: Implement in analytics service
        )

    async def _get_balance_overview(self, user_id: int) -> BalanceOverview:
        """Get balance overview."""
        total_balance = await self.account_repo.get_total_balance(user_id)
        
        accounts = await self.account_repo.get_user_accounts(
            user_id, include_inactive=False
        )
        
        return BalanceOverview(
            total_balance=total_balance,
            currency="RUB",
            change_amount=Decimal("0.00"),  # TODO: Calculate from previous period
            change_percentage=0.0,
            account_count=len(accounts),
        )

    async def _get_income_expense_summary(
        self, user_id: int, date_from: date, date_to: date
    ) -> IncomeExpenseSummary:
        """Get income/expense summary."""
        total_income = await self.transaction_repo.get_total_by_type(
            user_id, "income", date_from, date_to
        )
        
        total_expense = await self.transaction_repo.get_total_by_type(
            user_id, "expense", date_from, date_to
        )
        
        return IncomeExpenseSummary(
            total_income=total_income,
            total_expense=total_expense,
            net_amount=total_income - total_expense,
            income_count=0,  # TODO: Add count to repository
            expense_count=0,
        )

