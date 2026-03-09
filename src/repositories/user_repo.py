"""
User repository.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model."""

    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> User | None:
        """
        Get user by email.
        
        Args:
            email: User email
            
        Returns:
            User instance or None
        """
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        """
        Get user by username.
        
        Args:
            username: Username
            
        Returns:
            User instance or None
        """
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def email_exists(self, email: str, exclude_id: int | None = None) -> bool:
        """
        Check if email is already taken.
        
        Args:
            email: Email to check
            exclude_id: User ID to exclude from check (for updates)
            
        Returns:
            True if email exists, False otherwise
        """
        query = select(User).where(User.email == email)
        
        if exclude_id is not None:
            query = query.where(User.id != exclude_id)
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def username_exists(
        self, username: str, exclude_id: int | None = None
    ) -> bool:
        """
        Check if username is already taken.
        
        Args:
            username: Username to check
            exclude_id: User ID to exclude from check (for updates)
            
        Returns:
            True if username exists, False otherwise
        """
        query = select(User).where(User.username == username)
        
        if exclude_id is not None:
            query = query.where(User.id != exclude_id)
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_active_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """
        Get all active users.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of active users
        """
        result = await self.session.execute(
            select(User)
            .where(User.is_active == True)  # noqa: E712
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

