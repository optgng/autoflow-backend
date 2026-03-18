"""
Telegram service — генерация токенов и привязка аккаунтов.
"""
import secrets
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.models.telegram_link_token import TelegramLinkToken
from src.config import settings


class TelegramService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def generate_link_token(self, user_id: int) -> TelegramLinkToken:
        """Генерирует одноразовый токен для привязки Telegram."""

        # Инвалидируем старые неиспользованные токены этого пользователя
        old_tokens = await self.session.execute(
            select(TelegramLinkToken).where(
                TelegramLinkToken.user_id == user_id,
                TelegramLinkToken.used == False,
            )
        )
        for token in old_tokens.scalars().all():
            token.used = True
            self.session.add(token)

        # Создаём новый токен
        token = TelegramLinkToken(
            user_id    = user_id,
            token      = secrets.token_urlsafe(32),
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=10),
            used       = False,
        )
        self.session.add(token)
        await self.session.commit()
        await self.session.refresh(token)
        return token

    async def link_telegram(
        self,
        raw_token: str,
        telegram_id: int,
        telegram_username: str | None,
    ) -> User:
        """
        Привязывает telegram_id к пользователю по токену.
        Вызывается n8n после /start auth_TOKEN.
        """

        # Находим токен
        result = await self.session.execute(
            select(TelegramLinkToken).where(
                TelegramLinkToken.token == raw_token,
            )
        )
        link_token = result.scalar_one_or_none()

        if not link_token:
            raise ValueError("Токен не найден")

        if link_token.used:
            raise ValueError("Токен уже был использован")

        if link_token.expires_at < datetime.now(timezone.utc):
            raise ValueError("Токен истёк. Создайте новую ссылку на сайте")

        # Проверяем что этот telegram_id не привязан к другому пользователю
        existing = await self.session.execute(
            select(User).where(
                User.telegram_id == telegram_id,
            )
        )
        existing_user = existing.scalar_one_or_none()
        if existing_user and existing_user.id != link_token.user_id:
            raise ValueError("Этот Telegram аккаунт уже привязан к другому пользователю")

        # Находим пользователя и привязываем
        user_result = await self.session.execute(
            select(User).where(User.id == link_token.user_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            raise ValueError("Пользователь не найден")

        user.telegram_id       = telegram_id
        user.telegram_username = telegram_username

        # Помечаем токен использованным
        link_token.used = True

        self.session.add(user)
        self.session.add(link_token)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_status(self, user_id: int) -> User:
        """Возвращает текущий статус привязки."""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def unlink_telegram(self, user_id: int) -> None:
        """Отвязывает Telegram от аккаунта."""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if user:
            user.telegram_id       = None
            user.telegram_username = None
            self.session.add(user)
            await self.session.commit()

