from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from datetime import date, timedelta

from src.api.deps import CurrentUser, DBSession
from src.schemas.habit import HabitCreate, HabitUpdate, HabitResponse
from src.models.habit_log import HabitLog
from src.utils.streak import compute_current_streak
from src.utils.habit_strength import compute_habit_strength  # <-- новый импорт
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from src.repositories.habit_repo import HabitRepository
from src.repositories.habit_log_repo import HabitLogRepository
from src.models.habit import Habit
from src.models.habit_log import HabitLog

router = APIRouter(prefix="/habits", tags=["Habits"])


@router.get("/", response_model=List[HabitResponse])
async def get_habits(current_user: CurrentUser, session: DBSession):
    habit_repo = HabitRepository(session)
    start_date = date.today() - timedelta(days=14)
    return await habit_repo.get_user_habits_with_logs(current_user.id, start_date)


@router.post("/", response_model=HabitResponse, status_code=status.HTTP_201_CREATED)
async def create_habit(
    habit_in: HabitCreate, current_user: CurrentUser, session: DBSession
):
    habit_repo = HabitRepository(session)
    habit = await habit_repo.create(**habit_in.model_dump(), user_id=current_user.id)
    result = await session.execute(
        select(Habit).where(Habit.id == habit.id).options(selectinload(Habit.logs))
    )
    return result.scalar_one()


@router.post("/{habit_id}/toggle")
async def toggle_habit(
    habit_id: int,
    current_user: CurrentUser,
    session: DBSession,
    target_date: Optional[date] = Query(default=None),
):
    if target_date is None:
        target_date = date.today()

    result = await session.execute(
        select(Habit)
        .where(Habit.id == habit_id, Habit.user_id == current_user.id)
        .with_for_update()
        .options(selectinload(Habit.logs))
    )
    habit = result.scalar_one_or_none()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    log = next((l for l in habit.logs if l.date == target_date), None)
    if log:
        log.is_completed = not log.is_completed
        is_completed = log.is_completed
    else:
        log = HabitLog(habit_id=habit_id, date=target_date, is_completed=True)
        session.add(log)
        habit.logs.append(log)
        is_completed = True

    await session.flush()

    # Пересчёт стрейка и силы привычки
    habit.current_streak = compute_current_streak(habit.logs)
    habit.habit_strength = compute_habit_strength(habit.logs, target_date)

    await session.commit()

    return {
        "status": "ok",
        "is_completed": is_completed,
        "current_streak": habit.current_streak,
        "habit_strength": habit.habit_strength,
    }


@router.get("/activity/summary")
async def get_activity_summary(
    current_user: CurrentUser,
    session: DBSession,
    days: int = Query(default=7, ge=1, le=90),
):
    """Возвращает кол-во выполненных привычек за каждый из последних N дней."""
    today = date.today()
    date_from = today - timedelta(days=days - 1)

    result = await session.execute(
        select(HabitLog.date, func.count(HabitLog.id).label("count"))
        .join(Habit, HabitLog.habit_id == Habit.id)
        .where(
            Habit.user_id == current_user.id,
            HabitLog.is_completed == True,
            HabitLog.date >= date_from,
            HabitLog.date <= today,
        )
        .group_by(HabitLog.date)
    )
    completed_by_date = {row.date: row.count for row in result.all()}

    return [
        {
            "date": str(date_from + timedelta(days=i)),
            "count": completed_by_date.get(date_from + timedelta(days=i), 0),
        }
        for i in range(days)
    ]


@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_habit(habit_id: int, current_user: CurrentUser, session: DBSession):
    habit_repo = HabitRepository(session)
    habit = await habit_repo.get_by_id(id=habit_id)

    if not habit or habit.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found"
        )

    await habit_repo.delete(id=habit_id)
    return None
