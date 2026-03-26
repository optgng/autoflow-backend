from sqlalchemy import ForeignKey, String, Enum, Integer, Float
from sqlalchemy.types import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
import enum
from src.models.base import Base, TimestampMixin


class HabitFrequency(str, enum.Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    interval = "interval"


class HabitType(str, enum.Enum):
    good = "good"
    bad = "bad"


class Habit(Base, TimestampMixin):
    __tablename__ = "habits"
    __table_args__ = {"schema": "finances"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("finances.users.id", ondelete="CASCADE"), nullable=False
    )

    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    color: Mapped[str] = mapped_column(String, default="#3b82f6")
    icon: Mapped[str] = mapped_column(String, default="target")
    frequency: Mapped[HabitFrequency] = mapped_column(
        Enum(HabitFrequency, schema="finances"), default=HabitFrequency.daily
    )

    # Шаг 1
    current_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    habit_strength: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Шаг 2
    habit_type: Mapped[str] = mapped_column(String(10), default="good", nullable=False)
    time_of_day: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    repeat_days: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    logs: Mapped[list["HabitLog"]] = relationship(
        "HabitLog", back_populates="habit", cascade="all, delete-orphan"
    )
