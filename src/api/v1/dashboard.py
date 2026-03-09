"""
Transaction endpoints.
"""
from fastapi import APIRouter, HTTPException, Query, status

from src.api.deps import CurrentUser, DBSession
from src.core.exceptions import AuthorizationError, NotFoundError, ValidationError
from src.schemas.base import PaginatedResponse, PaginationParams
from src.schemas.transaction import (
    TransactionCreate,
    TransactionDetail,
    TransactionFilters,
    TransactionResponse,
    TransactionUpdate,
)
from src.services.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    data: TransactionCreate,
    current_user: CurrentUser,
    session: DBSession,
) -> TransactionResponse:
    """
    Create new transaction.
    
    Automatically updates account balance.
    Requires authentication.
    """
    try:
        service = TransactionService(session)
        return await service.create_transaction(current_user.id, data)
    except (NotFoundError, ValidationError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("", response_model=PaginatedResponse)
async def get_transactions(
    current_user: CurrentUser,
    session: DBSession,
    # Filters
    account_id: int | None = Query(None),
    category_id: int | None = Query(None),
    transaction_type: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    min_amount: float | None = Query(None),
    max_amount: float | None = Query(None),
    merchant: str | None = Query(None),
    search: str | None = Query(None),
    # Pagination
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedResponse:
    """
    Get transactions with filters and pagination.
    
    Requires authentication.
    """
    from datetime import date as date_type
    from decimal import Decimal
    
    # Parse dates
    date_from_parsed = date_type.fromisoformat(date_from) if date_from else None
    date_to_parsed = date_type.fromisoformat(date_to) if date_to else None
    
    filters = TransactionFilters(
        account_id=account_id,
        category_id=category_id,
        transaction_type=transaction_type,
        date_from=date_from_parsed,
        date_to=date_to_parsed,
        min_amount=Decimal(str(min_amount)) if min_amount else None,
        max_amount=Decimal(str(max_amount)) if max_amount else None,
        merchant=merchant,
        search=search,
    )
    
    pagination = PaginationParams(page=page, page_size=page_size)
    
    service = TransactionService(session)
    return await service.get_user_transactions(current_user.id, filters, pagination)


@router.get("/{transaction_id}", response_model=TransactionDetail)
async def get_transaction(
    transaction_id: int,
    current_user: CurrentUser,
    session: DBSession,
) -> TransactionDetail:
    """
    Get transaction by ID with details.
    
    Requires authentication and ownership.
    """
    try:
        service = TransactionService(session)
        return await service.get_transaction(transaction_id, current_user.id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.patch("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: int,
    data: TransactionUpdate,
    current_user: CurrentUser,
    session: DBSession,
) -> TransactionResponse:
    """
    Update transaction.
    
    Automatically adjusts account balances.
    Requires authentication and ownership.
    """
    try:
        service = TransactionService(session)
        return await service.update_transaction(transaction_id, current_user.id, data)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: int,
    current_user: CurrentUser,
    session: DBSession,
) -> None:
    """
    Delete transaction.
    
    Automatically reverts account balance changes.
    Requires authentication and ownership.
    """
    try:
        service = TransactionService(session)
        await service.delete_transaction(transaction_id, current_user.id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

