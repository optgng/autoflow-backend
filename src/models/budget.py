"""
Budget model for expense tracking.
"""
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin
from src.models.category import Category
from src.models.user import User


class Budget(Base, TimestampMixin):
    """Budget model for expense limits."""
    
    __tablename__ = "budgets"
    __table_args__ = {"schema": "finances"}
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("finances.users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("finances.categories.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="NULL for total budget",
    )
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    period_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="daily, weekly, monthly, yearly",
    )
    
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    category: Mapped["Category"] = relationship("Category")
    
    def __repr__(self) -> str:
        return f"<Budget(id={self.id}, name={self.name}, amount={self.amount})>"

