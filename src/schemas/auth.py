"""
Authentication Pydantic schemas.
"""
from pydantic import EmailStr, Field

from src.schemas.base import BaseSchema
from src.schemas.user import UserResponse


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


class LoginRequest(BaseSchema):
    """Запрос на вход."""
    
    email: EmailStr
    password: str = Field(min_length=1)


class RegisterRequest(BaseSchema):
    """Запрос на регистрацию."""
    
    email: EmailStr
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=100)
    full_name: str | None = Field(None, max_length=255)


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

