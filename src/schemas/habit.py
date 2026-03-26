from pydantic import BaseModel
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

class HabitLogResponse(BaseModel):
    id: int
    date: date
    is_completed: bool

    class Config:
        from_attributes = True

class HabitResponse(HabitBase):
    id: int
    user_id: int
    logs: List[HabitLogResponse] = []

    class Config:
        from_attributes = True
