"""
Pytest configuration and fixtures.
"""
import asyncio
from typing import AsyncGenerator, Generator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.config import settings
from src.core.database import get_async_session
from src.models.base import Base
from src.app import app

# Test database URL (используем отдельную БД для тестов)
TEST_DATABASE_URL = settings.DATABASE_URL.replace("/finance", "/finance_test")

# Create test engine
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async with TestSessionLocal() as session:
        yield session
    
    # Drop tables after test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client."""
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_async_session] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def authenticated_client(
    client: AsyncClient,
) -> AsyncGenerator[tuple[AsyncClient, dict], None]:
    """Create authenticated test client."""
    # Register user
    register_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPassword123",
        "full_name": "Test User",
    }
    
    response = await client.post("/api/v1/auth/register", json=register_data)
    assert response.status_code == 201
    
    data = response.json()
    access_token = data["tokens"]["access_token"]
    user = data["user"]
    
    # Add authorization header
    client.headers["Authorization"] = f"Bearer {access_token}"
    
    yield client, user

