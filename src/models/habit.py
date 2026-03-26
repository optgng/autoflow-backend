from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from src.models.base import Base, TimestampMixin

class HabitFrequency(str, enum.Enum):
    daily = "daily"
    weekly = "weekly"

class Habit(Base, TimestampMixin):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    color = Column(String, default="#3b82f6") # HEX
    icon = Column(String, default="target")
    frequency = Column(Enum(HabitFrequency), default=HabitFrequency.daily)

    logs = relationship("HabitLog", back_populates="habit", cascade="all, delete-orphan")
