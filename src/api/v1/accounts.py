"""
Account endpoints.
"""
from decimal import Decimal

from fastapi import APIRouter, HTTPException, status

from src.api.deps import CurrentUser, DBSession
from src.core.exceptions import AuthorizationError, NotFoundError, ValidationError
from src.schemas.account import AccountCreate, AccountResponse, AccountUpdate
from src.services.account_service import AccountService

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    data: AccountCreate,
    current_user: CurrentUser,
    session: DBSession,
) -> AccountResponse:
    """
    Create new account.
    
    Requires authentication.
    """
    service = AccountService(session)
    return await service.create_account(current_user.id, data)


@router.get("", response_model=list[AccountResponse])
async def get_accounts(
    current_user: CurrentUser,
    session: DBSession,
    include_inactive: bool = False,
) -> list[AccountResponse]:
    """
    Get all accounts for current user.
    
    Requires authentication.
    """
    service = AccountService(session)
    return await service.get_user_accounts(current_user.id, include_inactive)


@router.get("/total-balance")
async def get_total_balance(
    current_user: CurrentUser,
    session: DBSession,
    currency: str = "RUB",
) -> dict[str, Decimal]:
    """
    Get total balance for current user.
    
    Requires authentication.
    """
    service = AccountService(session)
    total = await service.get_total_balance(current_user.id, currency)
    return {"total_balance": total, "currency": currency}


@router.get("/by-type/{account_type}", response_model=list[AccountResponse])
async def get_accounts_by_type(
    account_type: str,
    current_user: CurrentUser,
    session: DBSession,
) -> list[AccountResponse]:
    """
    Get accounts by type.
    
    Requires authentication.
    """
    service = AccountService(session)
    return await service.get_accounts_by_type(current_user.id, account_type)


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: int,
    current_user: CurrentUser,
    session: DBSession,
) -> AccountResponse:
    """
    Get account by ID.
    
    Requires authentication and ownership.
    """
    try:
        service = AccountService(session)
        return await service.get_account(account_id, current_user.id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.patch("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: int,
    data: AccountUpdate,
    current_user: CurrentUser,
    session: DBSession,
) -> AccountResponse:
    """
    Update account.
    
    Requires authentication and ownership.
    """
    try:
        service = AccountService(session)
        return await service.update_account(account_id, current_user.id, data)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: int,
    current_user: CurrentUser,
    session: DBSession,
) -> None:
    """
    Delete account.
    
    Requires authentication and ownership.
    """
    try:
        service = AccountService(session)
        await service.delete_account(account_id, current_user.id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

