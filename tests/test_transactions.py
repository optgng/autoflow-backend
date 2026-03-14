"""
Tests for transaction endpoints.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_expense_transaction(authenticated_client):
    """Test creating expense transaction."""
    client, user = authenticated_client
    
    # Create account
    account_response = await client.post(
        "/api/v1/accounts",
        json={
            "name": "Test Account",
            "account_type": "card",
            "currency": "RUB",
            "balance": "10000.00",
        },
    )
    account_id = account_response.json()["id"]
    
    # Get category
    categories_response = await client.get("/api/v1/categories?category_type=expense")
    category_id = categories_response.json()[0]["id"]
    
    # Create transaction
    response = await client.post(
        "/api/v1/transactions",
        json={
            "account_id": account_id,
            "category_id": category_id,
            "transaction_date": "2026-03-10",
            "amount": "1500.00",
            "transaction_type": "expense",
            "description": "Test expense",
        },
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == "1500.00"
    assert data["transaction_type"] == "expense"
    
    # Verify balance updated
    account_check = await client.get(f"/api/v1/accounts/{account_id}")
    assert float(account_check.json()["balance"]) == 8500.00


@pytest.mark.asyncio
async def test_create_income_transaction(authenticated_client):
    """Test creating income transaction."""
    client, user = authenticated_client
    
    # Create account
    account_response = await client.post(
        "/api/v1/accounts",
        json={
            "name": "Test Account",
            "account_type": "card",
            "currency": "RUB",
            "balance": "10000.00",
        },
    )
    account_id = account_response.json()["id"]
    
    # Get income category
    categories_response = await client.get("/api/v1/categories?category_type=income")
    category_id = categories_response.json()[0]["id"]
    
    # Create transaction
    response = await client.post(
        "/api/v1/transactions",
        json={
            "account_id": account_id,
            "category_id": category_id,
            "transaction_date": "2026-03-10",
            "amount": "50000.00",
            "transaction_type": "income",
            "description": "Salary",
        },
    )
    
    assert response.status_code == 201
    
    # Verify balance updated
    account_check = await client.get(f"/api/v1/accounts/{account_id}")
    assert float(account_check.json()["balance"]) == 60000.00


@pytest.mark.asyncio
async def test_get_transactions_with_filters(authenticated_client):
    """Test getting transactions with filters."""
    client, user = authenticated_client
    
    # Create account and transactions
    account_response = await client.post(
        "/api/v1/accounts",
        json={
            "name": "Test Account",
            "account_type": "card",
            "currency": "RUB",
            "balance": "10000.00",
        },
    )
    account_id = account_response.json()["id"]
    
    category_response = await client.get("/api/v1/categories?category_type=expense")
    category_id = category_response.json()[0]["id"]
    
    # Create transaction
    await client.post(
        "/api/v1/transactions",
        json={
            "account_id": account_id,
            "category_id": category_id,
            "transaction_date": "2026-03-10",
            "amount": "1000.00",
            "transaction_type": "expense",
            "description": "Test",
        },
    )
    
    # Get with filters
    response = await client.get(
        f"/api/v1/transactions?account_id={account_id}&transaction_type=expense"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1


import pytest


@pytest.mark.asyncio
async def test_get_transaction_by_id(authenticated_client):
    client, _ = authenticated_client

    account_response = await client.post(
        "/api/v1/accounts",
        json={
            "name": "Tx Account",
            "account_type": "card",
            "currency": "RUB",
            "balance": "10000.00",
        },
    )
    account_id = account_response.json()["id"]

    categories_response = await client.get("/api/v1/categories?category_type=expense")
    category_id = categories_response.json()[0]["id"]

    create_response = await client.post(
        "/api/v1/transactions",
        json={
            "account_id": account_id,
            "category_id": category_id,
            "transaction_date": "2026-03-10",
            "amount": "1000.00",
            "transaction_type": "expense",
            "description": "Coffee",
        },
    )
    assert create_response.status_code == 201
    tx_id = create_response.json()["id"]

    response = await client.get(f"/api/v1/transactions/{tx_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == tx_id
    assert data["amount"] == "1000.00"


@pytest.mark.asyncio
async def test_get_transaction_not_found(authenticated_client):
    client, _ = authenticated_client

    response = await client.get("/api/v1/transactions/999999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_transaction(authenticated_client):
    client, _ = authenticated_client

    account_response = await client.post(
        "/api/v1/accounts",
        json={
            "name": "Update Tx Account",
            "account_type": "card",
            "currency": "RUB",
            "balance": "10000.00",
        },
    )
    account_id = account_response.json()["id"]

    categories_response = await client.get("/api/v1/categories?category_type=expense")
    category_id = categories_response.json()[0]["id"]

    create_response = await client.post(
        "/api/v1/transactions",
        json={
            "account_id": account_id,
            "category_id": category_id,
            "transaction_date": "2026-03-10",
            "amount": "1000.00",
            "transaction_type": "expense",
            "description": "Old description",
        },
    )
    tx_id = create_response.json()["id"]

    response = await client.patch(
        f"/api/v1/transactions/{tx_id}",
        json={
            "amount": "1500.00",
            "description": "Updated description",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == "1500.00"
    assert data["description"] == "Updated description"


@pytest.mark.asyncio
async def test_delete_transaction(authenticated_client):
    client, _ = authenticated_client

    account_response = await client.post(
        "/api/v1/accounts",
        json={
            "name": "Delete Tx Account",
            "account_type": "card",
            "currency": "RUB",
            "balance": "10000.00",
        },
    )
    account_id = account_response.json()["id"]

    categories_response = await client.get("/api/v1/categories?category_type=expense")
    category_id = categories_response.json()[0]["id"]

    create_response = await client.post(
        "/api/v1/transactions",
        json={
            "account_id": account_id,
            "category_id": category_id,
            "transaction_date": "2026-03-10",
            "amount": "1200.00",
            "transaction_type": "expense",
            "description": "To delete",
        },
    )
    tx_id = create_response.json()["id"]

    delete_response = await client.delete(f"/api/v1/transactions/{tx_id}")
    assert delete_response.status_code == 204

    get_response = await client.get(f"/api/v1/transactions/{tx_id}")
    assert get_response.status_code == 404

    # баланс должен откатиться
    account_check = await client.get(f"/api/v1/accounts/{account_id}")
    assert float(account_check.json()["balance"]) == 10000.00


@pytest.mark.asyncio
async def test_create_transaction_unauthorized(authenticated_client):
    client, _ = authenticated_client
    client.headers.pop("Authorization", None)

    response = await client.post(
        "/api/v1/transactions",
        json={
            "account_id": 1,
            "category_id": 1,
            "transaction_date": "2026-03-10",
            "amount": "100.00",
            "transaction_type": "expense",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_transaction_invalid_payload(authenticated_client):
    client, _ = authenticated_client

    response = await client.post(
        "/api/v1/transactions",
        json={
            "account_id": "not_int",
            "category_id": 1,
            "transaction_date": "bad-date",
            "amount": "not_decimal",
            "transaction_type": "expense",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_transaction_forbidden(authenticated_client):
    client, _ = authenticated_client

    # пользователь 1
    account_response = await client.post(
        "/api/v1/accounts",
        json={
            "name": "Owner Account",
            "account_type": "card",
            "currency": "RUB",
            "balance": "10000.00",
        },
    )
    account_id = account_response.json()["id"]

    categories_response = await client.get("/api/v1/categories?category_type=expense")
    category_id = categories_response.json()[0]["id"]

    tx_response = await client.post(
        "/api/v1/transactions",
        json={
            "account_id": account_id,
            "category_id": category_id,
            "transaction_date": "2026-03-10",
            "amount": "400.00",
            "transaction_type": "expense",
            "description": "Owner tx",
        },
    )
    tx_id = tx_response.json()["id"]

    # пользователь 2
    register_response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "tx_hacker@example.com",
            "username": "tx_hacker",
            "password": "Password123!",
            "full_name": "Tx Hacker",
        },
    )
    token = register_response.json()["tokens"]["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"

    response = await client.patch(
        f"/api/v1/transactions/{tx_id}",
        json={"description": "hacked"},
    )
    assert response.status_code in (403, 404)


@pytest.mark.asyncio
async def test_delete_transaction_forbidden(authenticated_client):
    client, _ = authenticated_client

    account_response = await client.post(
        "/api/v1/accounts",
        json={
            "name": "Owner Account",
            "account_type": "card",
            "currency": "RUB",
            "balance": "10000.00",
        },
    )
    account_id = account_response.json()["id"]

    categories_response = await client.get("/api/v1/categories?category_type=expense")
    category_id = categories_response.json()[0]["id"]

    tx_response = await client.post(
        "/api/v1/transactions",
        json={
            "account_id": account_id,
            "category_id": category_id,
            "transaction_date": "2026-03-10",
            "amount": "400.00",
            "transaction_type": "expense",
            "description": "Owner tx",
        },
    )
    tx_id = tx_response.json()["id"]

    register_response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "tx_hacker2@example.com",
            "username": "tx_hacker2",
            "password": "Password123!",
            "full_name": "Tx Hacker2",
        },
    )
    token = register_response.json()["tokens"]["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"

    response = await client.delete(f"/api/v1/transactions/{tx_id}")
    assert response.status_code in (403, 404)

