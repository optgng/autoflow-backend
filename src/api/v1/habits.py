from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import date, timedelta

from src.api.deps import CurrentUser, DBSession
from src.schemas.habit import HabitCreate, HabitUpdate, HabitResponse
from src.repositories.habit_repo import HabitRepository
from src.repositories.habit_log_repo import HabitLogRepository
from src.models.habit_log import HabitLog

router = APIRouter(prefix="/habits", tags=["Habits"])

@router.get("/", response_model=List[HabitResponse])
async def get_habits(current_user: CurrentUser, session: DBSession):
    # Инициализируем репозиторий здесь, передавая актуальную сессию БД
    habit_repo = HabitRepository(session)
    start_date = date.today() - timedelta(days=14)
    return await habit_repo.get_user_habits_with_logs(current_user.id, start_date)

@router.post("/", response_model=HabitResponse, status_code=status.HTTP_201_CREATED)
async def create_habit(habit_in: HabitCreate, current_user: CurrentUser, session: DBSession):
    habit_repo = HabitRepository(session)
    return await habit_repo.create(obj_in=habit_in.model_dump(), user_id=current_user.id)

@router.post("/{habit_id}/toggle")
async def toggle_habit(habit_id: int, current_user: CurrentUser, session: DBSession, target_date: date = date.today()):
    habit_repo = HabitRepository(session)
    log_repo = HabitLogRepository(session)
    
    habit = await habit_repo.get_by_id(id=habit_id)
    if not habit or habit.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")
        
    log = await log_repo.get_by_habit_and_date(habit_id, target_date)
    
    if log:
        log.is_completed = not log.is_completed
        await session.commit()
        return {"status": "updated", "is_completed": log.is_completed}
    else:
        new_log = HabitLog(habit_id=habit_id, date=target_date, is_completed=True)
        session.add(new_log)
        await session.commit()
        return {"status": "created", "is_completed": True}
