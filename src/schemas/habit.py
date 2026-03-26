from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date
from src.models.habit import HabitFrequency

class HabitBase(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = "#3b82f6"
    icon: Optional[str] = "target"
    frequency: HabitFrequency = HabitFrequency.daily

class HabitCreate(HabitBase):
    pass

class HabitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    frequency: Optional[HabitFrequency] = None
    current_streak: int = 0

class HabitLogResponse(BaseModel):
    id: int
    date: date
    is_completed: bool
    model_config = ConfigDict(from_attributes=True)

class HabitResponse(HabitBase):
    id: int
    user_id: int
    current_streak: int = 0
    logs: List[HabitLogResponse] = []
    model_config = ConfigDict(from_attributes=True)

