# src/repositories/habit_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from datetime import date
from src.models.habit import Habit
from src.repositories.base import BaseRepository


class HabitRepository(BaseRepository[Habit]):
    def __init__(self, session: AsyncSession):
        super().__init__(Habit, session)

    async def get_user_habits_with_logs(
        self, user_id: int, start_date: date
    ) -> list[Habit]:
        stmt = (
            select(Habit)
            .where(Habit.user_id == user_id)          # ← только user_id, никакого habit_id
            .options(selectinload(Habit.logs))
        )
        result = await self.session.execute(stmt)
        habits = list(result.scalars().all())

        # Фильтруем логи по дате уже в Python — selectinload уже загрузил всё
        for habit in habits:
            habit.logs = [log for log in habit.logs if log.date >= start_date]

        return habits
