from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List
from datetime import date
from src.models.habit import Habit
from src.repositories.base_repo import BaseRepository

class HabitRepository(BaseRepository[Habit]):
    def __init__(self):
        super().__init__(Habit)

    async def get_user_habits_with_logs(self, db: AsyncSession, user_id: int, start_date: date) -> List[Habit]:
        stmt = (
            select(Habit)
            .where(Habit.user_id == user_id)
            .options(
                selectinload(Habit.logs).and_(Habit.logs.property.mapper.class_.date >= start_date)
            )
        )
        result = await db.execute(stmt)
        return result.scalars().all()
