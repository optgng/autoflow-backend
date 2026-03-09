"""
Authentication service.
"""
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.core.exceptions import AuthenticationError, ConflictError, NotFoundError
from src.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from src.models.user import User
from src.repositories.category_repo import CategoryRepository
from src.repositories.user_repo import UserRepository
from src.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, Token
from src.schemas.user import UserResponse


class AuthService:
    """Service for authentication and authorization."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.category_repo = CategoryRepository(session)

    async def register(self, data: RegisterRequest) -> AuthResponse:
        """
        Register new user.
        
        Args:
            data: Registration data
            
        Returns:
            Auth response with user and tokens
            
        Raises:
            ConflictError: If email or username already exists
        """
        # Check if email exists
        if await self.user_repo.email_exists(data.email):
            raise ConflictError(f"Email {data.email} already registered")
        
        # Check if username exists
        if await self.user_repo.username_exists(data.username):
            raise ConflictError(f"Username {data.username} already taken")
        
        # Create user
        hashed_password = get_password_hash(data.password)
        user = await self.user_repo.create(
            email=data.email,
            username=data.username,
            full_name=data.full_name,
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=False,
        )
        
        # Create default categories for new user
        await self.category_repo.create_default_categories(user.id)
        await self.session.commit()
        
        # Generate tokens
        tokens = self._create_tokens(user.id)
        
        return AuthResponse(
            user=UserResponse.model_validate(user),
            tokens=tokens,
        )

    async def login(self, data: LoginRequest) -> AuthResponse:
        """
        Login user.
        
        Args:
            data: Login credentials
            
        Returns:
            Auth response with user and tokens
            
        Raises:
            AuthenticationError: If credentials are invalid
        """
        # Get user by email
        user = await self.user_repo.get_by_email(data.email)
        
        if not user:
            raise AuthenticationError("Invalid email or password")
        
        # Verify password
        if not verify_password(data.password, user.hashed_password):
            raise AuthenticationError("Invalid email or password")
        
        # Check if user is active
        if not user.is_active:
            raise AuthenticationError("User account is disabled")
        
        # Generate tokens
        tokens = self._create_tokens(user.id)
        
        return AuthResponse(
            user=UserResponse.model_validate(user),
            tokens=tokens,
        )

    async def refresh_token(self, refresh_token: str) -> Token:
        """
        Refresh access token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            New token pair
            
        Raises:
            AuthenticationError: If token is invalid
        """
        try:
            payload = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )
            
            user_id = payload.get("sub")
            token_type = payload.get("type")
            
            if not user_id or token_type != "refresh":
                raise AuthenticationError("Invalid refresh token")
            
            # Check if user exists and is active
            user = await self.user_repo.get_by_id(int(user_id))
            if not user or not user.is_active:
                raise AuthenticationError("User not found or disabled")
            
            # Generate new tokens
            return self._create_tokens(user.id)
            
        except JWTError:
            raise AuthenticationError("Invalid refresh token")

    async def get_current_user(self, token: str) -> User:
        """
        Get current user from access token.
        
        Args:
            token: Access token
            
        Returns:
            Current user
            
        Raises:
            AuthenticationError: If token is invalid
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )
            
            user_id = payload.get("sub")
            token_type = payload.get("type")
            
            if not user_id or token_type != "access":
                raise AuthenticationError("Invalid access token")
            
            user = await self.user_repo.get_by_id(int(user_id))
            
            if not user:
                raise NotFoundError("User not found")
            
            if not user.is_active:
                raise AuthenticationError("User account is disabled")
            
            return user
            
        except JWTError:
            raise AuthenticationError("Invalid access token")

    async def change_password(
        self, user_id: int, old_password: str, new_password: str
    ) -> bool:
        """
        Change user password.
        
        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password
            
        Returns:
            True if successful
            
        Raises:
            AuthenticationError: If old password is wrong
            NotFoundError: If user not found
        """
        user = await self.user_repo.get_by_id(user_id)
        
        if not user:
            raise NotFoundError("User not found")
        
        # Verify old password
        if not verify_password(old_password, user.hashed_password):
            raise AuthenticationError("Current password is incorrect")
        
        # Update password
        hashed_password = get_password_hash(new_password)
        await self.user_repo.update(user_id, hashed_password=hashed_password)
        
        return True

    def _create_tokens(self, user_id: int) -> Token:
        """Create access and refresh tokens."""
        access_token = create_access_token(str(user_id))
        refresh_token = create_refresh_token(str(user_id))
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

