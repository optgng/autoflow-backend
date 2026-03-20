"""
Account endpoints.
"""
from decimal import Decimal

from fastapi import APIRouter, HTTPException, status

from src.api.deps import CurrentUser, DBSession
from src.core.exceptions import AuthorizationError, NotFoundError, ValidationError
from src.schemas.account import AccountCreate, AccountResponse, AccountUpdate
from src.services.account_service import AccountService
from decimal import Decimal
from typing import Dict
from sqlalchemy import func, select
from src.models.account import Account

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    data: AccountCreate,
    current_user: CurrentUser,
    session: DBSession,
) -> AccountResponse:
    """
    Create new account.
    Только наличные (cash). Валидация типа — в схеме AccountCreate.
    """
    try:
        service = AccountService(session)
        return await service.create_account(current_user.id, data)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=list[AccountResponse])
async def get_accounts(
    current_user: CurrentUser,
    session: DBSession,
    include_inactive: bool = False,
) -> list[AccountResponse]:
    """Get all accounts for current user."""
    service = AccountService(session)
    return await service.get_user_accounts(current_user.id, include_inactive)


@router.get("/total-balance")
async def get_total_balance(
    current_user: CurrentUser,
    session: DBSession,
    currency: str = "RUB",
):
    """Get total balance for current user."""
    service = AccountService(session)
    total = await service.get_total_balance(current_user.id, currency)

    if total is None:
        total = Decimal("0.00")

    return {"total_balance": total, "currency": currency}


@router.get("/by-type/{account_type}", response_model=list[AccountResponse])
async def get_accounts_by_type(
    account_type: str,
    current_user: CurrentUser,
    session: DBSession,
) -> list[AccountResponse]:
    """Get accounts by type."""
    service = AccountService(session)
    return await service.get_accounts_by_type(current_user.id, account_type)

@router.get("/balances-by-currency")
async def get_balances_by_currency(
    current_user: CurrentUser,
    session: DBSession,
) -> Dict:
    """
    Суммарный баланс по каждой валюте отдельно.
    USD-наличные не суммируются с RUB — фронт отображает их раздельно.
    """
    result = await session.execute(
        select(Account.currency, func.sum(Account.balance))
        .where(Account.user_id == current_user.id)
        .where(Account.is_active == True)        # noqa: E712
        .where(Account.include_in_total == True)  # noqa: E712
        .group_by(Account.currency)
    )
    balances = {row[0]: str(row[1] or Decimal("0.00")) for row in result.all()}
    return {"balances": balances}


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: int,
    current_user: CurrentUser,
    session: DBSession,
) -> AccountResponse:
    """Get account by ID."""
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
    """Update account."""
    try:
        service = AccountService(session)
        return await service.update_account(account_id, current_user.id, data)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,   detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,   detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: int,
    current_user: CurrentUser,
    session: DBSession,
) -> None:
    """Delete account (soft delete for card/bank_account, hard for cash)."""
    try:
        service = AccountService(session)
        await service.delete_account(account_id, current_user.id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
