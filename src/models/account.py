"""
Account database model.
"""
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    DECIMAL,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.transaction import Transaction


class Account(Base):
    """Account model for storing user accounts (cards, wallets, etc)."""

    __tablename__ = "accounts"
    __table_args__ = {"schema": "finances"}
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("finances.users.id", ondelete="CASCADE"), nullable=False
    )

    # Account details
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    account_type: Mapped[str] = mapped_column(String(50), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="RUB")
    balance: Mapped[Decimal] = mapped_column(
        DECIMAL(15, 2), nullable=False, default=Decimal("0.00")
    )

    # Optional fields
    bank_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    account_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    last_four_digits: Mapped[str | None] = mapped_column(String(4), nullable=True)
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)
    color: Mapped[str | None] = mapped_column(String(7), nullable=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    include_in_total: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships - ИСПРАВЛЕНО: добавлен foreign_keys
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        back_populates="account",
        foreign_keys="Transaction.account_id",  # ← ИСПРАВЛЕНИЕ
        cascade="all, delete-orphan",
    )

    # Constraints
    __table_args__ = (
        CheckConstraint("balance >= 0", name="check_balance_positive"),
        CheckConstraint(
            "account_type IN ('card', 'bank_account', 'cash', 'investment', 'crypto', 'other')",
            name="check_account_type",
        ),
        Index("idx_accounts_user", "user_id"),
        Index("idx_accounts_type", "account_type"),
    )

    def __repr__(self) -> str:
        return f"<Account(id={self.id}, name={self.name}, balance={self.balance})>"

