from sqlalchemy import ForeignKey, String, Enum, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from src.models.base import Base, TimestampMixin

class HabitFrequency(str, enum.Enum):
    daily = "daily"
    weekly = "weekly"

class Habit(Base, TimestampMixin):
    __tablename__ = "habits"
    __table_args__ = {"schema": "finances"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("finances.users.id", ondelete="CASCADE"), nullable=False)
    
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    color: Mapped[str] = mapped_column(String, default="#3b82f6")
    icon: Mapped[str] = mapped_column(String, default="target")
    frequency: Mapped[HabitFrequency] = mapped_column(Enum(HabitFrequency), default=HabitFrequency.daily)
    
    current_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    logs: Mapped[list["HabitLog"]] = relationship("HabitLog", back_populates="habit", cascade="all, delete-orphan")
