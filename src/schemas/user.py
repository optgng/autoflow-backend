"""User Pydantic schemas — full version with SEC-12 and SEC-13 fixes."""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from src.schemas.base import BaseSchema, TimestampSchema


class UserBase(BaseSchema):
    email: EmailStr
    username: str
    full_name: str | None = None


class UserCreate(BaseModel):
    """Registration schema — used by AuthService."""
    email: EmailStr
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=100)
    full_name: str | None = Field(None, max_length=255)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        import re
        if not re.match(r"^[a-zA-Z0-9_-]{3,100}$", v):
            raise ValueError("Username may only contain letters, digits, _ and -")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        errors = []
        if len(v) < 8:
            errors.append("минимум 8 символов")
        if not any(c.isupper() for c in v):
            errors.append("хотя бы одна заглавная буква")
        if not any(c.islower() for c in v):
            errors.append("хотя бы одна строчная буква")
        if errors:
            raise ValueError(f"Пароль должен содержать: {', '.join(errors)}")
        return v


class UserUpdate(BaseSchema):
    """Profile update schema.
    SEC-13: password removed — use POST /auth/change-password instead.
    """
    username: str | None = Field(None, min_length=3, max_length=100)
    email: EmailStr | None = None
    full_name: str | None = Field(None, max_length=255)
    # NOTE: password intentionally omitted — use POST /auth/change-password


class UserResponse(UserBase, TimestampSchema):
    """Public user schema.
    SEC-12: is_superuser removed — use AdminUserResponse for internal use.
    """
    id: int
    is_active: bool
    telegram_id: int | None = None       # нужен в settings/page.tsx для отображения статуса
    telegram_username: str | None = None


class AdminUserResponse(UserResponse):
    """Internal admin schema — includes privileged fields (SEC-12)."""
    is_superuser: bool
    hashed_password: str | None = None   # только для отладки, никогда в API


class UserInDB(UserBase, TimestampSchema):
    """Internal schema with hashed password — never returned via API."""
    id: int
    is_active: bool
    is_superuser: bool
    hashed_password: str


class UserProfile(UserResponse):
    """Extended user profile with stats."""
    total_accounts: int = 0
    total_transactions: int = 0
