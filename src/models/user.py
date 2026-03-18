"""
User model.
"""
from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, String, Integer, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.models.account import Account


class User(Base, TimestampMixin):
    """User model."""
    
    __tablename__ = "users"
    __table_args__ = {"schema": "finances"}
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    telegram_id: Mapped[int | None] = mapped_column(
        BigInteger, nullable=True, unique=True, index=True
    )

    telegram_username: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    # Relationships
    accounts: Mapped[List["Account"]] = relationship(
        "Account",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    telegram_link_tokens: Mapped[list["TelegramLinkToken"]] = relationship(
        "TelegramLinkToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"

