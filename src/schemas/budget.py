"""
Budget Pydantic schemas.
"""
from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import Field, field_validator

from src.schemas.base import BaseSchema, TimestampSchema
from src.schemas.category import CategoryResponse


PeriodType = Literal["daily", "weekly", "monthly", "yearly"]


class BudgetBase(BaseSchema):
    """Базовые поля бюджета."""
    
    name: str = Field(min_length=1, max_length=255)
    amount: Decimal = Field(gt=0)
    period_type: PeriodType
    start_date: date
    end_date: date | None = None
    
    @field_validator("end_date")
    @classmethod
    def validate_dates(cls, v: date | None, info) -> date | None:
        """Проверка что end_date > start_date."""
        if v is not None and "start_date" in info.data:
            if v <= info.data["start_date"]:
                raise ValueError("end_date must be after start_date")
        return v


class BudgetCreate(BudgetBase):
    """Схема создания бюджета."""
    
    category_id: int | None = None


class BudgetUpdate(BaseSchema):
    """Схема обновления бюджета."""
    
    name: str | None = Field(None, min_length=1, max_length=255)
    amount: Decimal | None = Field(None, gt=0)
    period_type: PeriodType | None = None
    start_date: date | None = None
    end_date: date | None = None
    category_id: int | None = None


class BudgetInDB(BudgetBase, TimestampSchema):
    """Бюджет из БД."""
    
    id: int
    user_id: int
    category_id: int | None


class BudgetResponse(BudgetBase, TimestampSchema):
    """Бюджет для API ответа."""
    
    id: int
    category_id: int | None


class BudgetWithStats(BudgetResponse):
    """Бюджет со статистикой использования."""
    
    category: CategoryResponse | None = None
    spent_amount: Decimal = Decimal("0.00")
    remaining_amount: Decimal = Decimal("0.00")
    spent_percentage: float = 0.0
    is_exceeded: bool = False
    days_remaining: int = 0

