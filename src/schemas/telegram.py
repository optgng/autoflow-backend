"""
Telegram schemas.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class GenerateLinkResponse(BaseModel):
    """Ответ на генерацию deep link."""
    deep_link: str        # https://t.me/ИМЯ_БОТА?start=auth_TOKEN
    token: str            # сам токен (для отображения в UI если нужно)
    expires_at: datetime  # когда истекает


class TelegramLinkRequest(BaseModel):
    """n8n отправляет этот запрос после /start auth_TOKEN."""
    token: str
    telegram_id: int
    telegram_username: Optional[str] = None


class TelegramLinkResponse(BaseModel):
    """Ответ на успешную привязку."""
    success: bool
    message: str
    username: Optional[str] = None  # имя пользователя на платформе


class TelegramStatusResponse(BaseModel):
    """Статус привязки Telegram для UI."""
    is_linked: bool
    telegram_username: Optional[str] = None
    telegram_id: Optional[int] = None

