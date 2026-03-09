"""
Budget repository.
"""
from datetime import date
from decimal import Decimal

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.budget import Budget
from src.repositories.base import BaseRepository


class BudgetRepository(BaseRepository[Budget]):
    """Repository for Budget model."""

    def __init__(self, session: AsyncSession):
        super().__init__(Budget, session)

    async def get_user_budgets(
        self, user_id: int, active_only: bool = True
    ) -> list[Budget]:
        """
        Get all budgets for user.
        
        Args:
            user_id: User ID
            active_only: Only active budgets (within date range)
            
        Returns:
            List of budgets
        """
        query = select(Budget).where(Budget.user_id == user_id)
        
        if active_only:
            today = date.today()
            query = query.where(
                and_(
                    Budget.start_date <= today,
                    or_(Budget.end_date.is_(None), Budget.end_date >= today),
                )
            )
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_category(
        self, user_id: int, category_id: int
    ) -> Budget | None:
        """
        Get budget for specific category.
        
        Args:
            user_id: User ID
            category_id: Category ID
            
        Returns:
            Budget or None
        """
        result = await self.session.execute(
            select(Budget)
            .where(Budget.user_id == user_id)
            .where(Budget.category_id == category_id)
        )
        return result.scalar_one_or_none()

    async def get_spent_amount(
        self, budget_id: int, start_date: date, end_date: date | None = None
    ) -> Decimal:
        """
        Calculate spent amount for budget period.
        
        Args:
            budget_id: Budget ID
            start_date: Period start
            end_date: Period end
            
        Returns:
            Spent amount
        """
        from src.models.transaction import Transaction
        
        budget = await self.get_by_id(budget_id)
        if not budget:
            return Decimal("0.00")
        
        query = (
            select(func.sum(Transaction.amount))
            .where(Transaction.transaction_type == "expense")
            .where(Transaction.transaction_date >= start_date)
        )
        
        if end_date:
            query = query.where(Transaction.transaction_date <= end_date)
        
        if budget.category_id:
            query = query.where(Transaction.category_id == budget.category_id)
        
        result = await self.session.execute(query)
        total = result.scalar_one_or_none()
        return total if total is not None else Decimal("0.00")

