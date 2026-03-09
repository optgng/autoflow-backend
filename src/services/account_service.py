"""
Account service.
"""
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import AuthorizationError, NotFoundError, ValidationError
from src.repositories.account_repo import AccountRepository
from src.schemas.account import AccountCreate, AccountResponse, AccountUpdate, AccountWithStats


class AccountService:
    """Service for account management."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.account_repo = AccountRepository(session)

    async def create_account(
        self, user_id: int, data: AccountCreate
    ) -> AccountResponse:
        """
        Create new account.
        
        Args:
            user_id: Owner user ID
            data: Account data
            
        Returns:
            Created account
        """
        account = await self.account_repo.create(
            user_id=user_id,
            name=data.name,
            account_type=data.account_type,
            currency=data.currency,
            balance=data.balance,
            bank_name=data.bank_name,
            last_four_digits=data.last_four_digits,
            icon=data.icon,
            color=data.color,
            include_in_total=data.include_in_total,
            is_active=True,
        )
        
        return AccountResponse.model_validate(account)

    async def get_account(self, account_id: int, user_id: int) -> AccountResponse:
        """
        Get account by ID.
        
        Args:
            account_id: Account ID
            user_id: User ID (for authorization)
            
        Returns:
            Account
            
        Raises:
            NotFoundError: If account not found
            AuthorizationError: If user doesn't own account
        """
        account = await self.account_repo.get_by_id(account_id)
        
        if not account:
            raise NotFoundError("Account not found")
        
        if account.user_id != user_id:
            raise AuthorizationError("Access denied to this account")
        
        return AccountResponse.model_validate(account)

    async def get_user_accounts(
        self, user_id: int, include_inactive: bool = False
    ) -> list[AccountResponse]:
        """
        Get all accounts for user.
        
        Args:
            user_id: User ID
            include_inactive: Include inactive accounts
            
        Returns:
            List of accounts
        """
        accounts = await self.account_repo.get_user_accounts(
            user_id=user_id,
            include_inactive=include_inactive,
        )
        
        return [AccountResponse.model_validate(acc) for acc in accounts]

    async def update_account(
        self, account_id: int, user_id: int, data: AccountUpdate
    ) -> AccountResponse:
        """
        Update account.
        
        Args:
            account_id: Account ID
            user_id: User ID (for authorization)
            data: Update data
            
        Returns:
            Updated account
            
        Raises:
            NotFoundError: If account not found
            AuthorizationError: If user doesn't own account
        """
        account = await self.account_repo.get_by_id(account_id)
        
        if not account:
            raise NotFoundError("Account not found")
        
        if account.user_id != user_id:
            raise AuthorizationError("Access denied to this account")
        
        updated = await self.account_repo.update(
            account_id,
            **data.model_dump(exclude_unset=True),
        )
        
        return AccountResponse.model_validate(updated)

    async def delete_account(self, account_id: int, user_id: int) -> bool:
        """
        Delete account.
        
        Args:
            account_id: Account ID
            user_id: User ID (for authorization)
            
        Returns:
            True if deleted
            
        Raises:
            NotFoundError: If account not found
            AuthorizationError: If user doesn't own account
        """
        account = await self.account_repo.get_by_id(account_id)
        
        if not account:
            raise NotFoundError("Account not found")
        
        if account.user_id != user_id:
            raise AuthorizationError("Access denied to this account")
        
        return await self.account_repo.delete(account_id)

    async def get_total_balance(
        self, user_id: int, currency: str = "RUB"
    ) -> Decimal:
        """
        Get total balance for user.
        
        Args:
            user_id: User ID
            currency: Currency filter
            
        Returns:
            Total balance
        """
        return await self.account_repo.get_total_balance(user_id, currency)

    async def get_accounts_by_type(
        self, user_id: int, account_type: str
    ) -> list[AccountResponse]:
        """
        Get accounts by type.
        
        Args:
            user_id: User ID
            account_type: Account type
            
        Returns:
            List of accounts
        """
        accounts = await self.account_repo.get_by_type(user_id, account_type)
        return [AccountResponse.model_validate(acc) for acc in accounts]

