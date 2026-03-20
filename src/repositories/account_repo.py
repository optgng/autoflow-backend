"""
Account repository.
"""
from decimal import Decimal

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account import Account
from src.repositories.base import BaseRepository


class AccountRepository(BaseRepository[Account]):
    """Repository for Account model."""

    def __init__(self, session: AsyncSession):
        super().__init__(Account, session)

    async def get_user_accounts(
        self,
        user_id: int,
        include_inactive: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Account]:
        """
        Get all accounts for a user.
        
        Args:
            user_id: User ID
            include_inactive: Include inactive accounts
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of accounts
        """
        query = select(Account).where(Account.user_id == user_id)
        
        if not include_inactive:
            query = query.where(Account.is_active == True)  # noqa: E712
        
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_total_balance(
        self, user_id: int, currency: str = "RUB"
    ) -> Decimal:
        """
        Calculate total balance for user's accounts.
        
        Args:
            user_id: User ID
            currency: Currency filter
            
        Returns:
            Total balance
        """
        result = await self.session.execute(
            select(func.sum(Account.balance))
            .where(Account.user_id == user_id)
            .where(Account.currency == currency)
            .where(Account.is_active == True)  # noqa: E712
            .where(Account.include_in_total == True)  # noqa: E712
        )
        total = result.scalar_one_or_none()
        return total if total is not None else Decimal("0.00")

    async def get_by_type(
        self, user_id: int, account_type: str
    ) -> list[Account]:
        """
        Get accounts by type for a user.
        
        Args:
            user_id: User ID
            account_type: Account type
            
        Returns:
            List of accounts
        """
        result = await self.session.execute(
            select(Account)
            .where(Account.user_id == user_id)
            .where(Account.account_type == account_type)
            .where(Account.is_active == True)  # noqa: E712
        )
        return list(result.scalars().all())

    async def update_balance(
        self, account_id: int, amount: Decimal, operation: str = "add"
    ) -> Account | None:
        """
        Update account balance.
        
        Args:
            account_id: Account ID
            amount: Amount to add or subtract
            operation: 'add' or 'subtract'
            
        Returns:
            Updated account or None
        """
        account = await self.get_by_id(account_id)
        
        if account is None:
            return None
        
        if operation == "add":
            new_balance = account.balance + amount
        elif operation == "subtract":
            new_balance = account.balance - amount
        else:
            raise ValueError(f"Invalid operation: {operation}")
        
        if new_balance < 0:
            raise ValueError("Account balance cannot be negative")
        
        return await self.update(account_id, balance=new_balance)

    async def get_balances_by_currency(self, user_id: int) -> dict[str, Decimal]:
        """Суммы по каждой валюте для активных счетов пользователя."""
        result = await self.session.execute(
            select(Account.currency, func.sum(Account.balance))
            .where(Account.user_id == user_id)
            .where(Account.is_active == True)
            .where(Account.include_in_total == True)
            .group_by(Account.currency)
        )
        return {row[0]: (row[1] or Decimal("0.00")) for row in result.all()}

    async def get_by_account_number(
        self, user_id: int, account_number: str
    ) -> Account | None:
        """Поиск счёта по полному номеру."""
        result = await self.session.execute(
            select(Account).where(
                Account.user_id        == user_id,
                Account.account_number == account_number,
            )
        )
        return result.scalar_one_or_none()


    async def get_by_last_four(
        self, user_id: int, last4: str
    ) -> Account | None:
        """Поиск карты/счёта по последним 4 цифрам (только card/bank_account)."""
        result = await self.session.execute(
            select(Account).where(
                Account.user_id.in_([user_id]),
                Account.last_four_digits == last4,
                Account.account_type.in_(["card", "bank_account"]),
                Account.is_active == True,
            )
        )
        return result.scalar_one_or_none()


    async def update_account_number(
        self, account_id: int, account_number: str
    ) -> None:
        """Обновить полный номер счёта — вызывается из ImportService."""
        await self.session.execute(
            text("""
                UPDATE finances.accounts
                SET account_number = :account_number,
                    updated_at     = NOW()
                WHERE id = :id
            """),
            {"account_number": account_number, "id": account_id},
        )
