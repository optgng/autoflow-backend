from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models.habit_log import HabitLog
from src.repositories.base_repo import BaseRepository
from datetime import date

class HabitLogRepository(BaseRepository[HabitLog]):
    def __init__(self):
        super().__init__(HabitLog)

    async def get_by_habit_and_date(self, db: AsyncSession, habit_id: int, log_date: date) -> HabitLog | None:
        stmt = select(HabitLog).where(HabitLog.habit_id == habit_id, HabitLog.date == log_date)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
