import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_transaction_access_forbidden(authenticated_client):
    """Test 403 Forbidden when creating a transaction for someone else's account."""
    client, user1 = authenticated_client
    
    # 1. Пользователь 1 создает счет
    acc_resp = await client.post(
        "/api/v1/accounts",
        json={"name": "User 1 Account", "account_type": "card", "currency": "RUB", "balance": "1000.00"},
    )
    account_id = acc_resp.json()["id"]
    
    # 2. Регистрируем Пользователя 2
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "thief@example.com", "username": "thief1", "password": "Password123!", "full_name": "Thief"}
    )
    token_thief = reg_resp.json()["tokens"]["access_token"]
    
    # 3. Переключаемся на Пользователя 2
    client.headers["Authorization"] = f"Bearer {token_thief}"
    
    # Получаем любую доступную категорию Пользователя 2
    cat_resp = await client.get("/api/v1/categories?category_type=expense")
    category_id = cat_resp.json()[0]["id"]
    
    # 4. Пользователь 2 пытается списать деньги со счета Пользователя 1
    malicious_tx = await client.post(
        "/api/v1/transactions",
        json={
            "account_id": account_id,
            "category_id": category_id,
            "transaction_date": "2026-03-14",
            "amount": "500.00",
            "transaction_type": "expense",
            "description": "Stolen money",
        }
    )
    # Должно быть отклонено
    assert malicious_tx.status_code in (403, 404)

@pytest.mark.asyncio
async def test_create_transaction_invalid_amount(authenticated_client):
    """Test 422 Unprocessable Entity for invalid transaction amounts."""
    client, _ = authenticated_client
    
    acc_resp = await client.post(
        "/api/v1/accounts",
        json={"name": "Temp", "account_type": "card", "currency": "RUB"}
    )
    account_id = acc_resp.json()["id"]
    
    cat_resp = await client.get("/api/v1/categories?category_type=expense")
    category_id = cat_resp.json()[0]["id"]
    
    # Попытка создать транзакцию с отрицательной суммой
    resp_negative = await client.post(
        "/api/v1/transactions",
        json={
            "account_id": account_id,
            "category_id": category_id,
            "transaction_date": "2026-03-14",
            "amount": "-1500.00", # Невалидное значение
            "transaction_type": "expense",
        }
    )
    assert resp_negative.status_code == 422
