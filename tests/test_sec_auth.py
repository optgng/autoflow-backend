import pytest
from httpx import AsyncClient

# ==============================================================================
# ДОПОЛНИТЕЛЬНЫЕ ТЕСТЫ БЕЗОПАСНОСТИ (AUTH)
# ==============================================================================

@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """Test 400/409 error when registering with an existing email."""
    user_data = {
        "email": "duplicate@example.com",
        "username": "user1",
        "password": "Password123",
        "full_name": "Test User",
    }

    # Первая регистрация успешна
    await client.post("/api/v1/auth/register", json=user_data)

    # Вторая попытка с тем же email
    user_data["username"] = "user2" # меняем username, но оставляем email
    response = await client.post("/api/v1/auth/register", json=user_data)

    assert response.status_code in (400, 409)

@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Test 401 Unauthorized for wrong password."""
    # Регистрируем пользователя
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "login_test@example.com",
            "username": "login_test",
            "password": "CorrectPassword123",
            "full_name": "Login Test",
        },
    )

    # Пытаемся войти с неверным паролем
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "login_test@example.com",
            "password": "WrongPassword123"
        }
    )
    assert response.status_code == 401
    assert "token" not in response.json()

