"""
User Pydantic schemas.
"""
from pydantic import EmailStr, Field, field_validator

from src.schemas.base import BaseSchema, TimestampSchema


class UserBase(BaseSchema):
    """Базовые поля пользователя."""
    
    email: EmailStr
    username: str = Field(min_length=3, max_length=100)
    full_name: str | None = Field(None, max_length=255)


class UserCreate(UserBase):
    """Схема создания пользователя."""
    
    password: str = Field(min_length=8, max_length=100)
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Валидация пароля."""
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")
        return v


class UserUpdate(BaseSchema):
    """Схема обновления пользователя."""
    
    email: EmailStr | None = None
    username: str | None = Field(None, min_length=3, max_length=100)
    full_name: str | None = Field(None, max_length=255)
    password: str | None = Field(None, min_length=8, max_length=100)
    is_active: bool | None = None


class UserInDB(UserBase, TimestampSchema):
    """Пользователь из БД."""
    
    id: int
    is_active: bool
    is_superuser: bool
    hashed_password: str


class UserResponse(UserBase, TimestampSchema):
    """Пользователь для API ответа (без пароля)."""
    
    id: int
    is_active: bool
    is_superuser: bool


class UserProfile(UserResponse):
    """Профиль пользователя с дополнительной информацией."""
    
    total_accounts: int = 0
    total_transactions: int = 0

