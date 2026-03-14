"""
Transaction service.
"""
from datetime import date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import AuthorizationError, NotFoundError, ValidationError
from src.repositories.account_repo import AccountRepository
from src.repositories.category_repo import CategoryRepository
from src.repositories.transaction_repo import TransactionRepository
from src.schemas.base import PaginatedResponse, PaginationParams
from src.schemas.transaction import (
    TransactionCreate,
    TransactionDetail,
    TransactionFilters,
    TransactionResponse,
    TransactionUpdate,
)


class TransactionService:
    """Service for transaction management."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.transaction_repo = TransactionRepository(session)
        self.account_repo = AccountRepository(session)
        self.category_repo = CategoryRepository(session)

    async def create_transaction(
        self, user_id: int, data: TransactionCreate
    ) -> TransactionResponse:
        """
        Create new transaction with balance update.
        
        Args:
            user_id: User ID
            data: Transaction data
            
        Returns:
            Created transaction
            
        Raises:
            NotFoundError: If account/category not found
            AuthorizationError: If user doesn't own account
            ValidationError: If validation fails
        """
        # Verify account ownership
        account = await self.account_repo.get_by_id(data.account_id)
        if not account:
            raise NotFoundError("Account not found")
        
        if account.user_id != user_id:
            raise AuthorizationError("Access denied to this account")
        
        # Verify category if provided
        if data.category_id:
            category = await self.category_repo.get_by_id(data.category_id)
            if not category:
                raise NotFoundError("Category not found")
        
        # For transfers, verify target account
        if data.transaction_type == "transfer":
            if not data.target_account_id:
                raise ValidationError("Target account required for transfers")
            
            target_account = await self.account_repo.get_by_id(data.target_account_id)
            if not target_account:
                raise NotFoundError("Target account not found")
            
            if target_account.user_id != user_id:
                raise AuthorizationError("Access denied to target account")
            
            if data.account_id == data.target_account_id:
                raise ValidationError("Cannot transfer to the same account")
        
        # Create transaction
        transaction = await self.transaction_repo.create(
            user_id=user_id,
            account_id=data.account_id,
            category_id=data.category_id,
            transaction_date=data.transaction_date,
            amount=data.amount,
            transaction_type=data.transaction_type,
            description=data.description,
            notes=data.notes,
            merchant=data.merchant,
            location=data.location,
            tags=data.tags,
            target_account_id=data.target_account_id,
        )
        
        # Update account balance
        await self._update_balance_for_transaction(
            account_id=data.account_id,
            amount=data.amount,
            transaction_type=data.transaction_type,
            target_account_id=data.target_account_id,
        )
        
        await self.session.commit()
        
        return TransactionResponse.model_validate(transaction)

    async def get_transaction(
        self, transaction_id: int, user_id: int
    ) -> TransactionDetail:
        """
        Get transaction by ID with relationships.
        
        Args:
            transaction_id: Transaction ID
            user_id: User ID (for authorization)
            
        Returns:
            Transaction with details
            
        Raises:
            NotFoundError: If transaction not found
            AuthorizationError: If user doesn't own transaction
        """
        transaction = await self.transaction_repo.get_by_id(transaction_id)
        
        if not transaction:
            raise NotFoundError("Transaction not found")
        
        # Check ownership through account
        account = await self.account_repo.get_by_id(transaction.account_id)
        if account.user_id != user_id:
            raise AuthorizationError("Access denied to this transaction")
            
        # ПРИСВАИВАЕМ связи вручную (Fix бага валидации):
        transaction.account = account
        if transaction.category_id:
            # Импортируем репозиторий, если его еще нет в __init__
            from src.repositories.category_repo import CategoryRepository
            category_repo = CategoryRepository(self.session)
            transaction.category = await category_repo.get_by_id(transaction.category_id)
        else:
            transaction.category = None
            
        return TransactionDetail.model_validate(transaction)


    async def get_user_transactions(
        self,
        user_id: int,
        filters: TransactionFilters,
        pagination: PaginationParams,
    ) -> PaginatedResponse:
        """
        Get user transactions with filters and pagination.
        
        Args:
            user_id: User ID
            filters: Filter parameters
            pagination: Pagination parameters
            
        Returns:
            Paginated transactions
        """
        transactions = await self.transaction_repo.get_user_transactions(
            user_id=user_id,
            account_id=filters.account_id,
            category_id=filters.category_id,
            transaction_type=filters.transaction_type,
            date_from=filters.date_from,
            date_to=filters.date_to,
            skip=pagination.offset,
            limit=pagination.limit,
        )
        
        # Count total (simplified - could be optimized)
        total = len(transactions)  # In production, use separate count query
        
        items = [TransactionResponse.model_validate(tx) for tx in transactions]
        
        return PaginatedResponse.create(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
        )

    async def update_transaction(
        self, transaction_id: int, user_id: int, data: TransactionUpdate
    ) -> TransactionResponse:
        """
        Update transaction.
        
        Args:
            transaction_id: Transaction ID
            user_id: User ID (for authorization)
            data: Update data
            
        Returns:
            Updated transaction
            
        Raises:
            NotFoundError: If transaction not found
            AuthorizationError: If user doesn't own transaction
        """
        transaction = await self.transaction_repo.get_by_id(transaction_id)
        
        if not transaction:
            raise NotFoundError("Transaction not found")
        
        account = await self.account_repo.get_by_id(transaction.account_id)
        if account.user_id != user_id:
            raise AuthorizationError("Access denied to this transaction")
        
        # Revert old balance changes
        await self._revert_balance_for_transaction(transaction)
        
        # Update transaction
        updated = await self.transaction_repo.update(
            transaction_id,
            **data.model_dump(exclude_unset=True),
        )
        
        # Apply new balance changes
        await self._update_balance_for_transaction(
            account_id=updated.account_id,
            amount=updated.amount,
            transaction_type=updated.transaction_type,
            target_account_id=updated.target_account_id,
        )
        
        await self.session.commit()
        
        return TransactionResponse.model_validate(updated)

    async def delete_transaction(
        self, transaction_id: int, user_id: int
    ) -> bool:
        """
        Delete transaction and revert balance.
        
        Args:
            transaction_id: Transaction ID
            user_id: User ID (for authorization)
            
        Returns:
            True if deleted
            
        Raises:
            NotFoundError: If transaction not found
            AuthorizationError: If user doesn't own transaction
        """
        transaction = await self.transaction_repo.get_by_id(transaction_id)
        
        if not transaction:
            raise NotFoundError("Transaction not found")
        
        account = await self.account_repo.get_by_id(transaction.account_id)
        if account.user_id != user_id:
            raise AuthorizationError("Access denied to this transaction")
        
        # Revert balance changes
        await self._revert_balance_for_transaction(transaction)
        
        # Delete transaction
        deleted = await self.transaction_repo.delete(transaction_id)
        
        await self.session.commit()
        
        return deleted

    async def _update_balance_for_transaction(
        self,
        account_id: int,
        amount: Decimal,
        transaction_type: str,
        target_account_id: int | None = None,
    ) -> None:
        """Update account balance based on transaction."""
        if transaction_type == "income":
            await self.account_repo.update_balance(account_id, amount, "add")
        
        elif transaction_type == "expense":
            await self.account_repo.update_balance(account_id, amount, "subtract")
        
        elif transaction_type == "transfer" and target_account_id:
            # Subtract from source
            await self.account_repo.update_balance(account_id, amount, "subtract")
            # Add to target
            await self.account_repo.update_balance(target_account_id, amount, "add")

    async def _revert_balance_for_transaction(self, transaction) -> None:
        """Revert balance changes from transaction."""
        if transaction.transaction_type == "income":
            await self.account_repo.update_balance(
                transaction.account_id, transaction.amount, "subtract"
            )
        
        elif transaction.transaction_type == "expense":
            await self.account_repo.update_balance(
                transaction.account_id, transaction.amount, "add"
            )
        
        elif transaction.transaction_type == "transfer" and transaction.target_account_id:
            # Reverse: add to source
            await self.account_repo.update_balance(
                transaction.account_id, transaction.amount, "add"
            )
            # Subtract from target
            await self.account_repo.update_balance(
                transaction.target_account_id, transaction.amount, "subtract"
            )

