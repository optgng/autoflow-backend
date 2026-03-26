from sqlalchemy import ForeignKey, Date, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date
from src.models.base import Base

class HabitLog(Base):
    __tablename__ = "habit_logs"
    # Кортеж для комбинации Constraints и аргументов таблицы
    __table_args__ = (
        UniqueConstraint('habit_id', 'date', name='uq_habit_date'),
        {"schema": "finances"}
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # Ссылка на таблицу habits внутри схемы finances
    habit_id: Mapped[int] = mapped_column(ForeignKey("finances.habits.id", ondelete="CASCADE"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=True)

    habit: Mapped["Habit"] = relationship("Habit", back_populates="logs")
