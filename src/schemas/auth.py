"""
Authentication Pydantic schemas.
"""
import re
from typing import Optional
from pydantic import BaseModel, field_validator, EmailStr, Field
from src.schemas.base import BaseSchema
from src.schemas.user import UserResponse

EMAIL_REGEX = re.compile(
    r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
)
USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9_\-]{3,100}$')

def is_valid_email(value: str) -> bool:
    return bool(EMAIL_REGEX.match(value))


def is_valid_username(value: str) -> bool:
    return bool(USERNAME_REGEX.match(value))

class Token(BaseSchema):
    """JWT токен."""
    
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseSchema):
    """Payload JWT токена."""
    
    sub: str  # user_id
    exp: int
    type: str  # access | refresh

class LoginRequest(BaseModel):
    login:    str   # email или username — валидируется ниже
    password: str

    @field_validator('login')
    @classmethod
    def validate_login(cls, v: str) -> str:
        v = v.strip().lower()
        if not v:
            raise ValueError("Поле не может быть пустым")
        if '@' in v:
            if not EMAIL_REGEX.match(v):
                raise ValueError("Некорректный email. Ожидается формат: user@domain.com")
        else:
            if not USERNAME_REGEX.match(v):
                raise ValueError(
                    "Некорректный username. "
                    "Допускаются буквы, цифры, _ и -. "
                    "Длина от 3 до 100 символов"
                )
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Пароль не может быть пустым")
        return v

class RegisterRequest(BaseModel):
    email:     EmailStr  # Pydantic встроенный валидатор
    username:  str
    password:  str
    full_name: Optional[str] = None

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = v.strip()
        if not is_valid_username(v):
            raise ValueError(
                "Username может содержать только буквы, цифры, _ и -. "
                "Длина от 3 до 100 символов"
            )
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        errors = []
        if len(v) < 8:
            errors.append("минимум 8 символов")
        if not re.search(r'[A-Z]', v):
            errors.append("минимум одна заглавная буква")
        if not re.search(r'[a-z]', v):
            errors.append("минимум одна строчная буква")
        if not re.search(r'\d', v):
            errors.append("минимум одна цифра")
        if errors:
            raise ValueError(f"Пароль должен содержать: {', '.join(errors)}")
        return v


class AuthResponse(BaseSchema):
    """Ответ после успешной аутентификации."""
    
    user: UserResponse
    tokens: Token


class RefreshTokenRequest(BaseSchema):
    """Запрос на обновление токена."""
    
    refresh_token: str


class PasswordChangeRequest(BaseSchema):
    """Запрос на смену пароля."""
    
    old_password: str
    new_password: str = Field(min_length=8, max_length=100)

