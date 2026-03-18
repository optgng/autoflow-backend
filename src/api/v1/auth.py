"""
Authentication endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import CurrentUser, DBSession
from src.core.exceptions import AuthenticationError, ConflictError
from src.schemas.auth import (
    AuthResponse,
    LoginRequest,
    PasswordChangeRequest,
    RefreshTokenRequest,
    RegisterRequest,
    Token,
)
from src.schemas.user import UserResponse
from src.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    session: DBSession,
) -> AuthResponse:
    """
    Register new user.
    
    Returns user data and authentication tokens.
    """
    try:
        auth_service = AuthService(session)
        return await auth_service.register(data)
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.post("/login", response_model=AuthResponse)
async def login(
    data: LoginRequest,
    session: DBSession,
) -> AuthResponse:
    """
    Login user.
    Accepts email or username + password.
    """
    try:
        service = AuthService(session)          # ← экземпляр, не класс
        return await service.login(data)        # ← передаём весь объект
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )

@router.post("/refresh", response_model=Token)
async def refresh_token(
    data: RefreshTokenRequest,
    session: DBSession,
) -> Token:
    """
    Refresh access token using refresh token.
    
    Returns new token pair.
    """
    try:
        auth_service = AuthService(session)
        return await auth_service.refresh_token(data.refresh_token)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: CurrentUser,
) -> UserResponse:
    """
    Get current user information.
    
    Requires authentication.
    """
    return UserResponse.model_validate(current_user)


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    data: PasswordChangeRequest,
    current_user: CurrentUser,
    session: DBSession,
) -> None:
    """
    Change user password.
    
    Requires authentication.
    """
    try:
        auth_service = AuthService(session)
        await auth_service.change_password(
            user_id=current_user.id,
            old_password=data.old_password,
            new_password=data.new_password,
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

