"""Enrichment review queue and confirm endpoints (Block 3)."""
from datetime import date
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import CurrentUser, DBSession
from src.models.transaction import Transaction

router = APIRouter(prefix="/enrichment", tags=["Enrichment"])


class ReviewItem(BaseModel):
    transaction_id: int
    date: str
    amount: float
    tx_type: str
    contact_ref: str | None
    llm_suggestion: str | None
    llm_confidence: float | None
    review_reason: str | None
    quick_actions: list[dict]


class ReviewQueue(BaseModel):
    items: list[ReviewItem]
    total: int


class ConfirmRequest(BaseModel):
    relation_type: str
    user_label: str | None = None
    save_rule: bool = False


QUICK_ACTIONS = [
    {"label": "Обязательный платёж", "value": "obligatory"},
    {"label": "Взаиморасчёт", "value": "mutual"},
    {"label": "Долг (дал)", "value": "debt_given"},
    {"label": "Прочее", "value": "other"},
]


@router.get("/review", response_model=ReviewQueue)
async def get_review_queue(
    current_user: CurrentUser,
    session: DBSession,
    page: int = Query(1, ge=1),
    pagesize: int = Query(20, ge=1, le=100),
) -> ReviewQueue:
    """Транзакции, ожидающие подтверждения категории пользователем."""
    from src.models.account import Account
    query = (
        select(Transaction)
        .join(Account, Transaction.account_id == Account.id)
        .where(Account.user_id == current_user.id)
        .where(Transaction.review_status == "pending")
        .order_by(Transaction.transaction_date.desc())
        .offset((page - 1) * pagesize)
        .limit(pagesize)
    )
    count_query = (
        select(func.count(Transaction.id))
        .join(Account, Transaction.account_id == Account.id)
        .where(Account.user_id == current_user.id)
        .where(Transaction.review_status == "pending")
    )
    result = await session.execute(query)
    count_result = await session.execute(count_query)
    txs = result.scalars().all()
    total = count_result.scalar_one()

    items = [
        ReviewItem(
            transaction_id=tx.id,
            date=str(tx.transaction_date),
            amount=float(tx.amount),
            tx_type=tx.transaction_type,
            contact_ref=tx.contact_ref,
            llm_suggestion=tx.enriched_category,
            llm_confidence=float(tx.enrichment_confidence) if tx.enrichment_confidence else None,
            review_reason=None,  # stored separately in future
            quick_actions=QUICK_ACTIONS,
        )
        for tx in txs
    ]
    return ReviewQueue(items=items, total=total)


@router.post("/review/{transaction_id}/confirm", status_code=status.HTTP_200_OK)
async def confirm_review(
    transaction_id: int,
    data: ConfirmRequest,
    current_user: CurrentUser,
    session: DBSession,
) -> dict:
    """Пользователь подтверждает/уточняет категорию транзакции."""
    from src.models.account import Account
    # Ownership check
    tx_result = await session.execute(
        select(Transaction)
        .join(Account, Transaction.account_id == Account.id)
        .where(Transaction.id == transaction_id)
        .where(Account.user_id == current_user.id)
    )
    tx = tx_result.scalar_one_or_none()
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    await session.execute(
        update(Transaction)
        .where(Transaction.id == transaction_id)
        .values(
            review_status="confirmed",
            enrichment_source="user",
        )
    )

    # Update ContactProfile if contact_ref present
    if tx.contact_ref and data.user_label:
        from src.models.contact_profile import ContactProfile
        from sqlalchemy.dialects.postgresql import insert as pg_insert
        stmt = pg_insert(ContactProfile).values(
            telegram_id=current_user.telegram_id or 0,
            contact_ref=tx.contact_ref,
            relation_type=data.relation_type,
            user_label=data.user_label,
            tx_count=1,
        ).on_conflict_do_update(
            constraint="uq_contact_per_user",
            set_={
                "relation_type": data.relation_type,
                "user_label": data.user_label,
            },
        )
        await session.execute(stmt)

    await session.commit()
    return {"status": "confirmed", "transaction_id": transaction_id}
