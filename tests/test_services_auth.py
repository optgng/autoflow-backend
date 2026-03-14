import pytest
from unittest.mock import AsyncMock, MagicMock

from src.core.exceptions import AuthenticationError, ConflictError
from src.services.auth_service import AuthService
from src.schemas.auth import RegisterRequest, LoginRequest


@pytest.mark.asyncio
async def test_auth_service_register_duplicate_email():
    session = AsyncMock()
    service = AuthService(session)

    service.user_repo.email_exists = AsyncMock(return_value=True)
    service.user_repo.username_exists = AsyncMock(return_value=False)

    with pytest.raises(ConflictError):
        await service.register(
            RegisterRequest(
                email="dup@example.com",
                username="dup_user",
                password="Password123",
                full_name="Dup User",
            )
        )


@pytest.mark.asyncio
async def test_auth_service_register_duplicate_username():
    session = AsyncMock()
    service = AuthService(session)

    service.user_repo.email_exists = AsyncMock(return_value=False)
    service.user_repo.username_exists = AsyncMock(return_value=True)

    with pytest.raises(ConflictError):
        await service.register(
            RegisterRequest(
                email="ok@example.com",
                username="dup_user",
                password="Password123",
                full_name="Dup User",
            )
        )


@pytest.mark.asyncio
async def test_auth_service_login_user_not_found():
    session = AsyncMock()
    service = AuthService(session)

    service.user_repo.get_by_email = AsyncMock(return_value=None)

    with pytest.raises(AuthenticationError):
        await service.login(
            LoginRequest(email="nope@example.com", password="Password123")
        )


@pytest.mark.asyncio
async def test_auth_service_refresh_invalid_token():
    session = AsyncMock()
    service = AuthService(session)

    with pytest.raises(AuthenticationError):
        await service.refresh_token("bad.token.value")

