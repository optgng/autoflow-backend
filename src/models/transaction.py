"""
Transaction database model.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    DECIMAL,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.account import Account
    from src.models.category import Category


class Transaction(Base):
    """Transaction model."""

    __tablename__ = "transactions"
    __table_args__ = {"schema": "finances"}
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign keys
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("finances.users.id", ondelete="CASCADE"), nullable=False
    )
    account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("finances.accounts.id", ondelete="CASCADE"), nullable=False
    )
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("finances.categories.id", ondelete="SET NULL"), nullable=True
    )
    target_account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("finances.accounts.id", ondelete="SET NULL"), nullable=True
    )
    external_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        unique=True,   # дедупликация по auth_code
        index=True,
    )

    import_source: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="manual",  # 'manual' | 'sber_pdf'
    )
    # Transaction data
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[Decimal] = mapped_column(
        DECIMAL(15, 2), nullable=False, default=Decimal("0.00")
    )
    transaction_type: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Optional fields
    merchant: Mapped[str | None] = mapped_column(String(255), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tags: Mapped[str | None] = mapped_column(String(500), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    receipt_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships - ИСПРАВЛЕНО: добавлен foreign_keys
    account: Mapped["Account"] = relationship(
        "Account",
        back_populates="transactions",
        foreign_keys=[account_id],  # ← ИСПРАВЛЕНИЕ
    )
    
    category: Mapped["Category | None"] = relationship(
        "Category",
        back_populates="transactions",
    )

    target_account: Mapped["Account"] = relationship(
        "Account",
        foreign_keys=[target_account_id],  # ← ИСПРАВЛЕНИЕ
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "transaction_type IN ('income', 'expense', 'transfer')",
            name="check_transaction_type",
        ),
        CheckConstraint("amount >= 0", name="check_amount_positive"),
        Index("idx_transactions_user_date", "user_id", "transaction_date"),
        Index("idx_transactions_account", "account_id"),
        Index("idx_transactions_category", "category_id"),
        Index("idx_transactions_type", "transaction_type"),
    )

    def __repr__(self) -> str:
        return f"<Transaction(id={self.id}, type={self.transaction_type}, amount={self.amount})>"

