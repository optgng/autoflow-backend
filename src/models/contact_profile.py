"""ContactProfile — privacy-safe contact tracking via HMAC hashes."""
from datetime import date
from decimal import Decimal

from sqlalchemy import BigInteger, Date, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, TimestampMixin


class ContactProfile(Base, TimestampMixin):
    __tablename__ = "contact_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    contact_ref: Mapped[str] = mapped_column(String(24), nullable=False)
    relation_type: Mapped[str] = mapped_column(String(30), default="unknown", nullable=False)
    typical_amount_min: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    typical_amount_max: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    avg_frequency_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_seen_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    tx_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    user_label: Mapped[str | None] = mapped_column(String(50), nullable=True)  # "Аренда", "Мама" — NO full name

    __table_args__ = (
        UniqueConstraint("telegram_id", "contact_ref", name="uq_contact_per_user"),
        {"schema": "finances"},
    )
