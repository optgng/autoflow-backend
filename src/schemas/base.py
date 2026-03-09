"""
Base Pydantic schemas.
"""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    model_config = ConfigDict(
        from_attributes=True,  # Для работы с SQLAlchemy моделями
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class TimestampSchema(BaseSchema):
    """Schema with timestamps."""
    
    created_at: datetime
    updated_at: datetime


class PaginationParams(BaseModel):
    """Параметры пагинации."""
    
    page: int = 1
    page_size: int = 20
    
    @property
    def offset(self) -> int:
        """Вычислить offset для SQL."""
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """Вычислить limit для SQL."""
        return self.page_size


class PaginatedResponse(BaseSchema):
    """Обёртка для пагинированных ответов."""
    
    items: list[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    @classmethod
    def create(
        cls,
        items: list[Any],
        total: int,
        page: int,
        page_size: int,
    ) -> "PaginatedResponse":
        """Создать пагинированный ответ."""
        total_pages = (total + page_size - 1) // page_size
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

