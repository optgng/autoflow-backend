"""True Finance Metrics — enrichment-aware income/expense (Block 3)."""
from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import CurrentUser, DBSession
from src.models.transaction import Transaction

router = APIRouter(prefix="/metrics", tags=["Metrics"])


class PeriodSchema(BaseModel):
    from_: str
    to: str

    class Config:
        populate_by_name = True
        fields = {"from_": "from"}


class CategoryBreakdown(BaseModel):
    category: str
    amount: float


class MetricsBreakdown(BaseModel):
    income_by_type: dict[str, float]
    expenses_by_category: list[CategoryBreakdown]


class TrueMetricsResponse(BaseModel):
    period: dict
    true_income: float
    true_expenses: float
    to_assets: float
    obligatory_transfers: float
    true_savings: float
    savings_rate: float
    pending_review_count: int
    pending_review_amount: float
    breakdown: MetricsBreakdown


@router.get("/true", response_model=TrueMetricsResponse)
async def get_true_metrics(
    current_user: CurrentUser,
    session: DBSession,
    date_from: str = Query(...),
    date_to: str = Query(...),
) -> TrueMetricsResponse:
    """
    True income/expense metrics excluding internal transfers and
    enrichment-flagged transactions.
    """
    from src.models.account import Account

    uid = current_user.id
    d_from = date.fromisoformat(date_from)
    d_to = date.fromisoformat(date_to)

    def base_query(tx_type: str):
        return (
            select(func.coalesce(func.sum(Transaction.amount), 0))
            .join(Account, Transaction.account_id == Account.id)
            .where(Account.user_id == uid)
            .where(Transaction.transaction_type == tx_type)
            .where(Transaction.exclude_from_metrics == False)  # noqa: E712
            .where(Transaction.transaction_date >= d_from)
            .where(Transaction.transaction_date <= d_to)
        )

    # True Income: operational income only
    true_income_result = await session.execute(
        base_query("income").where(Transaction.income_type == "operational")
    )
    true_income = Decimal(str(true_income_result.scalar_one() or 0))

    # True Expenses: regular + subscription + oneoff
    true_expense_result = await session.execute(
        base_query("expense")
        .where(Transaction.expense_type.in_(["regular", "subscription", "oneoff"]))
        .with_only_columns(func.coalesce(func.sum(func.coalesce(Transaction.net_amount, Transaction.amount)), 0))
    )
    true_expenses = Decimal(str(true_expense_result.scalar_one() or 0))

    # To Assets: KARTA-VKLAD transfers
    assets_result = await session.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0))
        .join(Account, Transaction.account_id == Account.id)
        .where(Account.user_id == uid)
        .where(Transaction.enriched_category == "Внутренний перевод")
        .where(Transaction.transaction_type == "expense")
        .where(Transaction.transaction_date >= d_from)
        .where(Transaction.transaction_date <= d_to)
    )
    to_assets = Decimal(str(assets_result.scalar_one() or 0))

    # Obligatory transfers
    obligatory_result = await session.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0))
        .join(Account, Transaction.account_id == Account.id)
        .where(Account.user_id == uid)
        .where(Transaction.enriched_category == "Обязательные платежи")
        .where(Transaction.transaction_date >= d_from)
        .where(Transaction.transaction_date <= d_to)
    )
    obligatory_transfers = Decimal(str(obligatory_result.scalar_one() or 0))

    # Pending review
    pending_result = await session.execute(
        select(func.count(Transaction.id), func.coalesce(func.sum(Transaction.amount), 0))
        .join(Account, Transaction.account_id == Account.id)
        .where(Account.user_id == uid)
        .where(Transaction.review_status == "pending")
        .where(Transaction.transaction_date >= d_from)
        .where(Transaction.transaction_date <= d_to)
    )
    pending_row = pending_result.one()
    pending_count = int(pending_row[0])
    pending_amount = Decimal(str(pending_row[1] or 0))

    # Expense breakdown by category
    exp_breakdown_result = await session.execute(
        select(Transaction.enriched_category, func.sum(Transaction.amount))
        .join(Account, Transaction.account_id == Account.id)
        .where(Account.user_id == uid)
        .where(Transaction.transaction_type == "expense")
        .where(Transaction.exclude_from_metrics == False)  # noqa: E712
        .where(Transaction.transaction_date >= d_from)
        .where(Transaction.transaction_date <= d_to)
        .where(Transaction.enriched_category.isnot(None))
        .group_by(Transaction.enriched_category)
        .order_by(func.sum(Transaction.amount).desc())
    )
    exp_breakdown = [
        CategoryBreakdown(category=row[0], amount=float(row[1]))
        for row in exp_breakdown_result.all()
    ]

    true_savings = true_income - true_expenses
    savings_rate = round(float(true_savings / true_income * 100), 1) if true_income > 0 else 0.0

    return TrueMetricsResponse(
        period={"from": date_from, "to": date_to},
        true_income=float(true_income),
        true_expenses=float(true_expenses),
        to_assets=float(to_assets),
        obligatory_transfers=float(obligatory_transfers),
        true_savings=float(true_savings),
        savings_rate=savings_rate,
        pending_review_count=pending_count,
        pending_review_amount=float(pending_amount),
        breakdown=MetricsBreakdown(
            income_by_type={"operational": float(true_income)},
            expenses_by_category=exp_breakdown,
        ),
    )
