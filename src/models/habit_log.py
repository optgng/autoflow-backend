from sqlalchemy import Column, Integer, ForeignKey, Date, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from src.models.base import Base

class HabitLog(Base):
    __tablename__ = "habit_logs"

    id = Column(Integer, primary_key=True, index=True)
    habit_id = Column(Integer, ForeignKey("habits.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    is_completed = Column(Boolean, default=True)

    __table_args__ = (
        UniqueConstraint('habit_id', 'date', name='uq_habit_date'),
    )

    habit = relationship("Habit", back_populates="logs")
