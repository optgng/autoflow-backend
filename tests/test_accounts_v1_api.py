import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_accounts_unauthorized(authenticated_client):
    """Test 401 Unauthorized accessing accounts without valid token."""
    client, _ = authenticated_client
    
    # Удаляем токен из заголовков для эмуляции неавторизованного запроса
    client.headers.pop("Authorization", None)
    
    response_get = await client.get("/api/v1/accounts")
    assert response_get.status_code == 401
    
    response_post = await client.post(
        "/api/v1/accounts",
        json={"name": "Ghost Account", "account_type": "card", "currency": "RUB"}
    )
    assert response_post.status_code == 401

@pytest.mark.asyncio
async def test_account_access_forbidden(authenticated_client):
    """Test 403 Forbidden accessing someone else's account."""
    client, user1 = authenticated_client
    
    # 1. Пользователь 1 создает счет
    create_response = await client.post(
        "/api/v1/accounts",
        json={"name": "User 1 Secret Account", "account_type": "card", "currency": "RUB", "balance": "100.00"},
    )
    account_id = create_response.json()["id"]
    
    # 2. Регистрируем Пользователя 2
    register_response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "hacker@example.com",
            "username": "hacker2",
            "password": "Password123!",
            "full_name": "Hacker User",
        }
    )
    token_hacker = register_response.json()["tokens"]["access_token"]
    
    # 3. Переключаем клиента на Пользователя 2
    client.headers["Authorization"] = f"Bearer {token_hacker}"
    
    # 4. Проверяем, что Пользователь 2 не может взаимодействовать со счетом Пользователя 1
    get_resp = await client.get(f"/api/v1/accounts/{account_id}")
    assert get_resp.status_code == 403
    
    patch_resp = await client.patch(f"/api/v1/accounts/{account_id}", json={"name": "Hacked Account"})
    assert patch_resp.status_code == 403
    
    del_resp = await client.delete(f"/api/v1/accounts/{account_id}")
    assert del_resp.status_code == 403

@pytest.mark.asyncio
async def test_create_account_invalid_data(authenticated_client):
    """Test 422 Unprocessable Entity for invalid payloads."""
    client, _ = authenticated_client
    
    # Отсутствие обязательного поля 'currency'
    resp_incomplete = await client.post(
        "/api/v1/accounts",
        json={}
    )
    assert resp_incomplete.status_code == 422
    
    # Неверный тип данных (буквы вместо баланса)
    resp_invalid_type = await client.post(
        "/api/v1/accounts",
        json={"name": "String Balance", "account_type": "card", "currency": "RUB", "balance": "not_a_number"}
    )
    assert resp_invalid_type.status_code == 422

@pytest.mark.asyncio
async def test_sql_injection_attempt(authenticated_client):
    """Test resilience against basic SQL injection strings."""
    client, _ = authenticated_client
    
    # SQLAlchemy и FastAPI экранируют данные, запрос должен либо пройти (сохранив как строку), либо отбиться 422
    malicious_payload = "'; DROP TABLE accounts; --"
    response = await client.post(
        "/api/v1/accounts",
        json={
            "name": malicious_payload,
            "account_type": "card",
            "currency": "RUB",
        }
    )
    assert response.status_code in (201, 422)

@pytest.mark.asyncio
async def test_get_account_not_found(authenticated_client):
    """Test 404 Not Found."""
    client, _ = authenticated_client
    response = await client.get("/api/v1/accounts/9999999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_accounts_by_type(authenticated_client):
    """Test functionally missing endpoint /by-type/{account_type}."""
    client, _ = authenticated_client
    
    await client.post(
        "/api/v1/accounts",
        json={"name": "My Cash", "account_type": "cash", "currency": "RUB"}
    )
    
    response = await client.get("/api/v1/accounts/by-type/cash")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) >= 1
    assert all(acc["account_type"] == "cash" for acc in data)

@pytest.mark.asyncio
async def test_get_total_balance_empty(authenticated_client):
    """Test total balance correctly returning 0.00 for empty accounts."""
    client, _ = authenticated_client
    response = await client.get("/api/v1/accounts/total-balance?currency=RUB")
    
    assert response.status_code == 200
    assert float(response.json()["total_balance"]) == 0.00
