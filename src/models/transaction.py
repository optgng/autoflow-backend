"""Transaction model with enrichment fields (Block 3)."""
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean, CheckConstraint, Date, DateTime, ForeignKey,
    Index, Integer, Numeric, String, Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.account import Account
    from src.models.category import Category


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = {"schema": "finances"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("finances.users.id", ondelete="CASCADE"), nullable=False)
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey("finances.accounts.id", ondelete="CASCADE"), nullable=False)
    category_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("finances.categories.id", ondelete="SET NULL"), nullable=True)
    target_account_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("finances.accounts.id", ondelete="SET NULL"), nullable=True)
    external_id: Mapped[str | None] = mapped_column(String(100), nullable=True, unique=True, index=True)
    import_source: Mapped[str] = mapped_column(String(20), nullable=False, server_default="manual")

    transaction_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=Decimal("0.00"))
    transaction_type: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    merchant: Mapped[str | None] = mapped_column(String(255), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tags: Mapped[str | None] = mapped_column(String(500), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    receipt_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ── Enrichment fields (added in migration 002_enrichment) ──────────────────
    enriched_category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    enriched_subcategory: Mapped[str | None] = mapped_column(String(100), nullable=True)
    enriched_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    income_type: Mapped[str | None] = mapped_column(String(50), nullable=True)   # operational|oneoff|return|internal
    expense_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # regular|subscription|oneoff|investment|debt_payment
    exclude_from_metrics: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_group_payment: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    net_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    linked_tx_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("finances.transactions.id"), nullable=True)
    enrichment_source: Mapped[str | None] = mapped_column(String(20), nullable=True)   # rule|llm|user
    enrichment_confidence: Mapped[Decimal | None] = mapped_column(Numeric(3, 2), nullable=True)
    review_status: Mapped[str] = mapped_column(String(20), default="auto", nullable=False)  # auto|pending|confirmed|rejected
    user_rule_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    enriched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    contact_ref: Mapped[str | None] = mapped_column(String(24), nullable=True, index=True)

    # ── Relationships ───────────────────────────────────────────────────────────
    account: Mapped["Account"] = relationship("Account", back_populates="transactions", foreign_keys=[account_id])
    category: Mapped["Category | None"] = relationship("Category", back_populates="transactions")
    target_account: Mapped["Account | None"] = relationship("Account", foreign_keys=[target_account_id])

    __table_args__ = (
        CheckConstraint("transaction_type IN ('income', 'expense', 'transfer')", name="check_transaction_type"),
        CheckConstraint("amount > 0", name="check_amount_positive"),
        Index("idx_transactions_user_date", "user_id", "transaction_date"),
        Index("idx_transactions_account", "account_id"),
        Index("idx_transactions_category", "category_id"),
        Index("idx_transactions_type", "transaction_type"),
        Index("idx_transactions_review_status", "review_status"),
        Index("idx_transactions_contact_ref", "contact_ref"),
        {"schema": "finances"},
    )
