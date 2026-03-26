from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import date, timedelta
from src.core.database import get_db
from src.core.security import get_current_user
from src.models.user import User
from src.schemas.habit import HabitCreate, HabitUpdate, HabitResponse
from src.repositories.habit_repo import HabitRepository
from src.repositories.habit_log_repo import HabitLogRepository
from src.models.habit_log import HabitLog

router = APIRouter(prefix="/habits", tags=["Habits"])
habit_repo = HabitRepository()
log_repo = HabitLogRepository()

@router.get("/", response_model=List[HabitResponse])
async def get_habits(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    start_date = date.today() - timedelta(days=14)
    return await habit_repo.get_user_habits_with_logs(db, current_user.id, start_date)

@router.post("/", response_model=HabitResponse)
async def create_habit(habit_in: HabitCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await habit_repo.create(db, obj_in=habit_in.model_dump(), user_id=current_user.id)

@router.post("/{habit_id}/toggle")
async def toggle_habit(habit_id: int, target_date: date = date.today(), db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    habit = await habit_repo.get(db, id=habit_id)
    if not habit or habit.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Habit not found")
        
    log = await log_repo.get_by_habit_and_date(db, habit_id, target_date)
    if log:
        log.is_completed = not log.is_completed
        await db.commit()
        return {"status": "updated", "is_completed": log.is_completed}
    else:
        new_log = HabitLog(habit_id=habit_id, date=target_date, is_completed=True)
        db.add(new_log)
        await db.commit()
        return {"status": "created", "is_completed": True}
