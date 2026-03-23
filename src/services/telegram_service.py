"""Telegram service with atomic token consumption (SEC-01, SEC-10)."""
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.models.telegram_link_token import TelegramLinkToken
from src.config import settings


class TelegramService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def generate_link_token(self, user_id: int) -> TelegramLinkToken:
        """Generate a new Telegram link token (invalidates old ones)."""
        old_tokens = await self.session.execute(
            select(TelegramLinkToken).where(
                TelegramLinkToken.user_id == user_id,
                TelegramLinkToken.used == False,  # noqa: E712
            )
        )
        for token in old_tokens.scalars().all():
            token.used = True
            self.session.add(token)

        token = TelegramLinkToken(
            user_id=user_id,
            token=secrets.token_urlsafe(32),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
            used=False,
        )
        self.session.add(token)
        await self.session.commit()
        await self.session.refresh(token)
        return token

    async def link_telegram(
        self,
        raw_token: str,
        telegram_id: int,
        telegram_username: str | None = None,
    ) -> User:
        """
        Atomically consume token and link Telegram (SEC-10).
        Uses UPDATE...WHERE used=FALSE RETURNING to prevent race conditions.
        """
        stmt = (
            update(TelegramLinkToken)
            .where(
                TelegramLinkToken.token == raw_token,
                TelegramLinkToken.used == False,  # noqa: E712
                TelegramLinkToken.expires_at > datetime.now(timezone.utc),
            )
            .values(used=True)
            .returning(TelegramLinkToken)
        )
        result = await self.session.execute(stmt)
        link_token = result.scalar_one_or_none()
        if not link_token:
            # Do NOT reveal whether token is invalid vs expired (SEC-01)
            raise ValueError("Invalid or expired token")

        # Check telegram_id not already linked to another user
        existing = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        existing_user = existing.scalar_one_or_none()
        if existing_user and existing_user.id != link_token.user_id:
            raise ValueError("Invalid or expired token")

        user_result = await self.session.execute(
            select(User).where(User.id == link_token.user_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            raise ValueError("Invalid or expired token")

        user.telegram_id = telegram_id
        user.telegram_username = telegram_username
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_status(self, user_id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def unlink_telegram(self, user_id: int) -> None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.telegram_id = None
            user.telegram_username = None
            self.session.add(user)
            await self.session.commit()
