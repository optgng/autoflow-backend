"""Auth endpoints with rate limiting (SEC-02)."""
from fastapi import APIRouter, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.api.deps import CurrentUser, DBSession
from src.core.exceptions import AuthenticationError, ConflictError
from src.schemas.auth import AuthResponse, LoginRequest, PasswordChangeRequest, RefreshTokenRequest, RegisterRequest, Token
from src.schemas.user import UserResponse
from src.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("3/hour")  # SEC-02: 3 registrations per hour per IP
async def register(request: Request, data: RegisterRequest, session: DBSession) -> AuthResponse:
    try:
        auth_service = AuthService(session)
        return await auth_service.register(data)
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/login", response_model=AuthResponse)
@limiter.limit("10/minute")  # SEC-02: 10 attempts per minute per IP
async def login(request: Request, data: LoginRequest, session: DBSession) -> AuthResponse:
    """Авторизация по email/username + пароль."""
    try:
        service = AuthService(session)
        return await service.login(data)
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/refresh", response_model=Token)
@limiter.limit("30/minute")  # SEC-02
async def refresh_token(request: Request, data: RefreshTokenRequest, session: DBSession) -> Token:
    try:
        auth_service = AuthService(session)
        return await auth_service.refresh_token(data.refresh_token)
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: CurrentUser) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    data: PasswordChangeRequest, current_user: CurrentUser, session: DBSession
) -> None:
    try:
        auth_service = AuthService(session)
        await auth_service.change_password(
            user_id=current_user.id,
            old_password=data.old_password,
            new_password=data.new_password,
        )
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
