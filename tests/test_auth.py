"""
Tests for authentication endpoints.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    """Test successful user registration."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "Password123",
            "full_name": "New User",
        },
    )
    
    assert response.status_code == 201
    data = response.json()
    
    assert "user" in data
    assert "tokens" in data
    assert data["user"]["email"] == "newuser@example.com"
    assert data["user"]["username"] == "newuser"
    assert "hashed_password" not in data["user"]
    assert data["tokens"]["access_token"]
    assert data["tokens"]["refresh_token"]


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """Test registration with duplicate email."""
    user_data = {
        "email": "duplicate@example.com",
        "username": "user1",
        "password": "Password123",
    }
    
    # First registration
    response1 = await client.post("/api/v1/auth/register", json=user_data)
    assert response1.status_code == 201
    
    # Second registration with same email
    user_data["username"] = "user2"
    response2 = await client.post("/api/v1/auth/register", json=user_data)
    assert response2.status_code == 409
    assert "already registered" in response2.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_weak_password(client: AsyncClient):
    """Test registration with weak password."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "weak",  # Too short
        },
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(authenticated_client):
    """Test successful login."""
    client, user = authenticated_client
    
    # Login with same credentials
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "TestPassword123",
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["email"] == "test@example.com"
    assert data["tokens"]["access_token"]


@pytest.mark.asyncio
async def test_login_wrong_password(authenticated_client):
    """Test login with wrong password."""
    client, _ = authenticated_client
    
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "WrongPassword123",
        },
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(authenticated_client):
    """Test getting current user info."""
    client, user = authenticated_client
    
    response = await client.get("/api/v1/auth/me")
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user["email"]
    assert data["username"] == user["username"]


@pytest.mark.asyncio
async def test_get_current_user_unauthorized(client: AsyncClient):
    """Test getting current user without token."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401

