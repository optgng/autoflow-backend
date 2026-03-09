"""
Category model for transactions.
"""
from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.models.transaction import Transaction
    from src.models.user import User


class Category(Base, TimestampMixin):
    """Transaction category model."""
    
    __tablename__ = "categories"
    __table_args__ = {"schema": "finances"}
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("finances.users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="NULL for system categories",
    )
    
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="income, expense, transfer",
    )
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)
    color: Mapped[str | None] = mapped_column(String(7), nullable=True)
    
    is_system: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="System category (cannot be deleted by user)",
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction",
        back_populates="category",
    )
    
    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name={self.name}, type={self.category_type})>"

