from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from datetime import date
from src.models.habit import Habit
from src.repositories.base import BaseRepository

class HabitRepository(BaseRepository[Habit]):
    def __init__(self, session: AsyncSession):
        super().__init__(Habit, session) # Передаем модель и сессию в базовый класс

    async def get_user_habits_with_logs(self, user_id: int, start_date: date) -> list[Habit]:
        stmt = (
            select(Habit)
            .where(Habit.user_id == user_id)
            .options(
                selectinload(Habit.logs).and_(Habit.logs.property.mapper.class_.date >= start_date)
            )
        )
        result = await self.session.execute(stmt) # Используем self.session
        return list(result.scalars().all())
