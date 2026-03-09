"""
Category Pydantic schemas.
"""
from typing import Literal

from pydantic import Field

from src.schemas.base import BaseSchema, TimestampSchema


CategoryType = Literal["income", "expense", "transfer"]


class CategoryBase(BaseSchema):
    """Базовые поля категории."""
    
    name: str = Field(min_length=1, max_length=100)
    category_type: CategoryType
    icon: str | None = Field(None, max_length=50)
    color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")


class CategoryCreate(CategoryBase):
    """Схема создания категории."""
    pass


class CategoryUpdate(BaseSchema):
    """Схема обновления категории."""
    
    name: str | None = Field(None, min_length=1, max_length=100)
    category_type: CategoryType | None = None
    icon: str | None = Field(None, max_length=50)
    color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    is_active: bool | None = None


class CategoryInDB(CategoryBase, TimestampSchema):
    """Категория из БД."""
    
    id: int
    user_id: int | None
    is_system: bool
    is_active: bool


class CategoryResponse(CategoryBase, TimestampSchema):
    """Категория для API ответа."""
    
    id: int
    is_system: bool
    is_active: bool


class CategoryWithStats(CategoryResponse):
    """Категория со статистикой использования."""
    
    transaction_count: int = 0
    total_amount: str = "0.00"  # Decimal as string for JSON

