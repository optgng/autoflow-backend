"""
Tests for account endpoints.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_account(authenticated_client):
    """Test creating account."""
    client, user = authenticated_client
    
    response = await client.post(
        "/api/v1/accounts",
        json={
            "name": "Test Account",
            "account_type": "card",
            "currency": "RUB",
            "balance": "10000.00",
        },
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Account"
    assert data["balance"] == "10000.00"
    assert data["currency"] == "RUB"


@pytest.mark.asyncio
async def test_get_accounts(authenticated_client):
    """Test getting all accounts."""
    client, user = authenticated_client
    
    # Create account
    await client.post(
        "/api/v1/accounts",
        json={
            "name": "Account 1",
            "account_type": "card",
            "currency": "RUB",
            "balance": "5000.00",
        },
    )
    
    # Get accounts
    response = await client.get("/api/v1/accounts")
    
    assert response.status_code == 200
    accounts = response.json()
    assert len(accounts) >= 1
    assert accounts[0]["name"] == "Account 1"


@pytest.mark.asyncio
async def test_get_total_balance(authenticated_client):
    """Test getting total balance."""
    client, user = authenticated_client
    
    # Create two accounts
    await client.post(
        "/api/v1/accounts",
        json={
            "name": "Account 1",
            "account_type": "card",
            "currency": "RUB",
            "balance": "10000.00",
        },
    )
    
    await client.post(
        "/api/v1/accounts",
        json={
            "name": "Account 2",
            "account_type": "card",
            "currency": "RUB",
            "balance": "5000.00",
        },
    )
    
    # Get total balance
    response = await client.get("/api/v1/accounts/total-balance?currency=RUB")
    
    assert response.status_code == 200
    data = response.json()
    assert float(data["total_balance"]) == 15000.00


@pytest.mark.asyncio
async def test_update_account(authenticated_client):
    """Test updating account."""
    client, user = authenticated_client
    
    # Create account
    create_response = await client.post(
        "/api/v1/accounts",
        json={
            "name": "Old Name",
            "account_type": "card",
            "currency": "RUB",
            "balance": "1000.00",
        },
    )
    account_id = create_response.json()["id"]
    
    # Update account
    response = await client.patch(
        f"/api/v1/accounts/{account_id}",
        json={"name": "New Name"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Name"


@pytest.mark.asyncio
async def test_delete_account(authenticated_client):
    """Test deleting account."""
    client, user = authenticated_client
    
    # Create account
    create_response = await client.post(
        "/api/v1/accounts",
        json={
            "name": "To Delete",
            "account_type": "card",
            "currency": "RUB",
            "balance": "1000.00",
        },
    )
    account_id = create_response.json()["id"]
    
    # Delete account
    response = await client.delete(f"/api/v1/accounts/{account_id}")
    assert response.status_code == 204
    
    # Verify deleted
    get_response = await client.get(f"/api/v1/accounts/{account_id}")
    assert get_response.status_code == 404

