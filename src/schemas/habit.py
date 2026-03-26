from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List, Literal
from datetime import date
from src.models.habit import HabitFrequency


# Допустимые значения для time_of_day и habit_type
TimeOfDayValue = Literal["morning", "afternoon", "evening"]
HabitTypeValue = Literal["good", "bad"]


class HabitBase(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = "#3b82f6"
    icon: Optional[str] = "target"
    frequency: HabitFrequency = HabitFrequency.daily

    # Новые поля
    habit_type: HabitTypeValue = "good"
    time_of_day: Optional[List[TimeOfDayValue]] = None
    repeat_days: Optional[List[int]] = None  # [0..6], 0 = Пн

    @field_validator("repeat_days")
    @classmethod
    def validate_repeat_days(cls, v: Optional[List[int]]) -> Optional[List[int]]:
        if v is not None:
            for day in v:
                if day < 0 or day > 6:
                    raise ValueError("repeat_days must contain values between 0 and 6")
        return v


class HabitCreate(HabitBase):
    pass


class HabitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    frequency: Optional[HabitFrequency] = None
    current_streak: int = 0
    habit_type: Optional[HabitTypeValue] = None
    time_of_day: Optional[List[TimeOfDayValue]] = None
    repeat_days: Optional[List[int]] = None


class HabitLogResponse(BaseModel):
    id: int
    date: date
    is_completed: bool
    model_config = ConfigDict(from_attributes=True)


class HabitResponse(HabitBase):
    id: int
    user_id: int
    current_streak: int = 0
    habit_strength: float = 0.0
    logs: List[HabitLogResponse] = []
    model_config = ConfigDict(from_attributes=True)
