"""
Legacy models for reading existing finance.* tables.
Эти модели ТОЛЬКО ДЛЯ ЧТЕНИЯ, не управляются Alembic.
"""
from datetime import date, time
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Boolean, Date, String, Time, Numeric, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class LegacyUser(Base):
    """Existing finance.users table (read-only)."""
    
    __tablename__ = "users"
    __table_args__ = {"schema": "finance", "extend_existing": True}
    
    id: Mapped[UUID] = mapped_column(primary_key=True)
    telegram_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    username: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    def __repr__(self) -> str:
        return f"<LegacyUser(id={self.id}, email={self.email})>"


class LegacyAccount(Base):
    """Existing finance.accounts table (read-only)."""
    
    __tablename__ = "accounts"
    __table_args__ = {"schema": "finance", "extend_existing": True}
    
    id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(nullable=False)
    account_number: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    bank_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(10), nullable=True)
    is_active: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    
    def __repr__(self) -> str:
        return f"<LegacyAccount(id={self.id}, name={self.name})>"


class LegacyTransaction(Base):
    """Existing finance.finance_transactions table (read-only)."""
    
    __tablename__ = "finance_transactions"
    __table_args__ = {"schema": "finance", "extend_existing": True}
    
    id: Mapped[int] = mapped_column(primary_key=True)
    account_number: Mapped[str] = mapped_column(String(50), nullable=False)
    date_msk: Mapped[date] = mapped_column(Date, nullable=False)
    time_msk: Mapped[time] = mapped_column(Time, nullable=False)
    auth_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    category: Mapped[str | None] = mapped_column(String(255), nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    tx_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    balance: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    date_operation: Mapped[date | None] = mapped_column(Date, nullable=True)
    merchant: Mapped[str | None] = mapped_column(nullable=True)
    
    def __repr__(self) -> str:
        return f"<LegacyTransaction(id={self.id}, amount={self.amount})>"

