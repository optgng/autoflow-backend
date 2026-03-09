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

