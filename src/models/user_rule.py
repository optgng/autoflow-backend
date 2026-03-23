"""User-defined enrichment rules."""
from sqlalchemy import BigInteger, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, TimestampMixin


class UserEnrichmentRule(Base, TimestampMixin):
    __tablename__ = "user_enrichment_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    rule_type: Mapped[str] = mapped_column(String(50), nullable=False)  # merchant_keyword|contact_ref|amount_range|combined
    match_pattern: Mapped[str] = mapped_column(String(200), nullable=False)
    action_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=10, nullable=False)

    __table_args__ = {"schema": "finances"}
