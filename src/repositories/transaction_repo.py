"""
Transaction repository.
"""
from datetime import date
from decimal import Decimal

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.transaction import Transaction
from src.repositories.base import BaseRepository


class TransactionRepository(BaseRepository[Transaction]):
    """Repository for Transaction model."""

    def __init__(self, session: AsyncSession):
        super().__init__(Transaction, session)

    async def get_user_transactions(
        self,
        user_id: int,
        account_id: int | None = None,
        category_id: int | None = None,
        transaction_type: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Transaction]:
        """
        Get transactions with filters.
        
        Args:
            user_id: User ID (for security)
            account_id: Filter by account
            category_id: Filter by category
            transaction_type: Filter by type
            date_from: Start date
            date_to: End date
            skip: Offset
            limit: Limit
            
        Returns:
            List of transactions
        """
        from src.models.account import Account
        
        query = (
            select(Transaction)
            .join(Account, Transaction.account_id == Account.id)
            .where(Account.user_id == user_id)
            .options(
                selectinload(Transaction.account),
                selectinload(Transaction.category),
                selectinload(Transaction.target_account),
            )
        )
        
        if account_id:
            query = query.where(Transaction.account_id == account_id)
        
        if category_id:
            query = query.where(Transaction.category_id == category_id)
        
        if transaction_type:
            query = query.where(Transaction.transaction_type == transaction_type)
        
        if date_from:
            query = query.where(Transaction.transaction_date >= date_from)
        
        if date_to:
            query = query.where(Transaction.transaction_date <= date_to)
        
        query = query.order_by(Transaction.transaction_date.desc(), Transaction.id.desc())
        query = query.offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_total_by_type(
        self,
        user_id: int,
        transaction_type: str,
        date_from: date | None = None,
        date_to: date | None = None,
        account_id: int | None = None,
    ) -> Decimal:
        """
        Get total amount by transaction type.
        
        Args:
            user_id: User ID
            transaction_type: Transaction type
            date_from: Start date
            date_to: End date
            account_id: Filter by account
            
        Returns:
            Total amount
        """
        from src.models.account import Account
        
        query = (
            select(func.sum(Transaction.amount))
            .join(Account, Transaction.account_id == Account.id)
            .where(Account.user_id == user_id)
            .where(Transaction.transaction_type == transaction_type)
        )
        
        if date_from:
            query = query.where(Transaction.transaction_date >= date_from)
        
        if date_to:
            query = query.where(Transaction.transaction_date <= date_to)
        
        if account_id:
            query = query.where(Transaction.account_id == account_id)
        
        result = await self.session.execute(query)
        total = result.scalar_one_or_none()
        return total if total is not None else Decimal("0.00")

    async def get_by_category(
        self,
        user_id: int,
        category_id: int,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> list[Transaction]:
        """
        Get transactions by category.
        
        Args:
            user_id: User ID
            category_id: Category ID
            date_from: Start date
            date_to: End date
            
        Returns:
            List of transactions
        """
        from src.models.account import Account
        
        query = (
            select(Transaction)
            .join(Account, Transaction.account_id == Account.id)
            .where(Account.user_id == user_id)
            .where(Transaction.category_id == category_id)
        )
        
        if date_from:
            query = query.where(Transaction.transaction_date >= date_from)
        
        if date_to:
            query = query.where(Transaction.transaction_date <= date_to)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def search_transactions(
        self,
        user_id: int,
        search_term: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Transaction]:
        """
        Search transactions by description or merchant.
        
        Args:
            user_id: User ID
            search_term: Search term
            skip: Offset
            limit: Limit
            
        Returns:
            List of transactions
        """
        from src.models.account import Account
        
        query = (
            select(Transaction)
            .join(Account, Transaction.account_id == Account.id)
            .where(Account.user_id == user_id)
            .where(
                or_(
                    Transaction.description.ilike(f"%{search_term}%"),
                    Transaction.merchant.ilike(f"%{search_term}%"),
                    Transaction.notes.ilike(f"%{search_term}%"),
                )
            )
            .order_by(Transaction.transaction_date.desc())
            .offset(skip)
            .limit(limit)
        )
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_recent_transactions(
        self, user_id: int, limit: int = 10
    ) -> list[Transaction]:
        """
        Get recent transactions for user.
        
        Args:
            user_id: User ID
            limit: Number of transactions
            
        Returns:
            List of recent transactions
        """
        from src.models.account import Account
        
        query = (
            select(Transaction)
            .join(Account, Transaction.account_id == Account.id)
            .where(Account.user_id == user_id)
            .options(
                selectinload(Transaction.account),
                selectinload(Transaction.category),
            )
            .order_by(Transaction.created_at.desc())
            .limit(limit)
        )
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def count_user_transactions(
        self,
        user_id: int,
        account_id: int | None = None,
        category_id: int | None = None,
        transaction_type: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> int:
        from src.models.account import Account
        query = (
            select(func.count(Transaction.id))
            .join(Account, Transaction.account_id == Account.id)
            .where(Account.user_id == user_id)
        )
        if account_id:
            query = query.where(Transaction.account_id == account_id)
        if category_id:
            query = query.where(Transaction.category_id == category_id)
        if transaction_type:
            query = query.where(Transaction.transaction_type == transaction_type)
        if date_from:
            query = query.where(Transaction.transaction_date >= date_from)
        if date_to:
            query = query.where(Transaction.transaction_date <= date_to)
        result = await self.session.execute(query)
        return result.scalar_one()


