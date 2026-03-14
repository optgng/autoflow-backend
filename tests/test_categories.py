"""
Tests for category endpoints.
"""
import pytest
from httpx import AsyncClient

# ==============================================================================
# БАЗОВЫЕ СЦЕНАРИИ (HAPPY PATH)
# ==============================================================================

@pytest.mark.asyncio
async def test_create_and_get_custom_category(authenticated_client):
    """Test creating a custom category and retrieving it."""
    client, user = authenticated_client
    
    # 1. Создаем кастомную категорию
    create_resp = await client.post(
        "/api/v1/categories",
        json={
            "name": "Мое Хобби",
            "category_type": "expense",
            "icon": "gamepad",
            "color": "#FF0000"
        }
    )
    assert create_resp.status_code == 201
    created_data = create_resp.json()
    assert created_data["name"] == "Мое Хобби"
    assert created_data["is_system"] is False
    
    # 2. Получаем список категорий пользователя (без системных)
    get_resp = await client.get("/api/v1/categories?include_system=false")
    assert get_resp.status_code == 200
    categories = get_resp.json()
    
    # Убеждаемся, что в ответе есть только что созданная категория и нет системных
    assert any(c["id"] == created_data["id"] for c in categories)
    assert all(c["is_system"] is False for c in categories)

# ==============================================================================
# БЕЗОПАСНОСТЬ: СИСТЕМНЫЕ КАТЕГОРИИ И ЧУЖИЕ ДАННЫЕ
# ==============================================================================

@pytest.mark.asyncio
async def test_modify_system_category_forbidden(authenticated_client):
    """Test 403 Forbidden when trying to update or delete a system category."""
    client, user = authenticated_client
    
    # Получаем список системных категорий
    get_resp = await client.get("/api/v1/categories?include_system=true")
    system_categories = [c for c in get_resp.json() if c.get("is_system") is True]
    
    # Если в БД есть системные категории, пытаемся их взломать
    if system_categories:
        sys_cat_id = system_categories[0]["id"]
        
        # Попытка изменения
        patch_resp = await client.patch(
            f"/api/v1/categories/{sys_cat_id}",
            json={"name": "Hacked System Name"}
        )
        assert patch_resp.status_code == 403
        
        # Попытка удаления
        delete_resp = await client.delete(f"/api/v1/categories/{sys_cat_id}")
        assert delete_resp.status_code == 403

@pytest.mark.asyncio
async def test_access_other_user_category_forbidden(authenticated_client):
    """Test 403/404 when trying to access another user's custom category."""
    client, user1 = authenticated_client
    
    # 1. Пользователь 1 создает свою категорию
    cat_resp = await client.post(
        "/api/v1/categories",
        json={"name": "User 1 Secret Category", "category_type": "expense"}
    )
    user1_cat_id = cat_resp.json()["id"]
    
    # 2. Регистрируем Пользователя 2 и получаем его токен
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "hacker_cat@example.com",
            "username": "hacker_cat",
            "password": "Password123!",
            "full_name": "Hacker Cat",
        }
    )
    token_hacker = reg_resp.json()["tokens"]["access_token"]
    
    # 3. Переключаемся на Пользователя 2
    client.headers["Authorization"] = f"Bearer {token_hacker}"
    
    # 4. Пользователь 2 пытается переименовать или удалить категорию Пользователя 1
    patch_resp = await client.patch(
        f"/api/v1/categories/{user1_cat_id}",
        json={"name": "Stolen Category"}
    )
    assert patch_resp.status_code in (403, 404)
    
    delete_resp = await client.delete(f"/api/v1/categories/{user1_cat_id}")
    assert delete_resp.status_code in (403, 404)

@pytest.mark.asyncio
async def test_category_validation_error(authenticated_client):
    """Test 422 Unprocessable Entity for missing required fields."""
    client, user = authenticated_client
    
    # Отсутствует обязательное поле category_type
    resp = await client.post(
        "/api/v1/categories",
        json={"name": "Invalid Category"}
    )
    assert resp.status_code == 422

import pytest


@pytest.mark.asyncio
async def test_create_category(authenticated_client):
    client, _ = authenticated_client

    response = await client.post(
        "/api/v1/categories",
        json={
            "name": "Custom Food",
            "category_type": "expense",
            "icon": "utensils",
            "color": "#FF0000",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Custom Food"
    assert data["category_type"] == "expense"


@pytest.mark.asyncio
async def test_get_categories_default(authenticated_client):
    client, _ = authenticated_client

    response = await client.get("/api/v1/categories")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_get_categories_filtered(authenticated_client):
    client, _ = authenticated_client

    response = await client.get("/api/v1/categories?category_type=income")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(item["category_type"] == "income" for item in data)


@pytest.mark.asyncio
async def test_get_categories_without_system(authenticated_client):
    client, _ = authenticated_client

    await client.post(
        "/api/v1/categories",
        json={
            "name": "Only Mine",
            "category_type": "expense",
            "icon": "tag",
            "color": "#00FF00",
        },
    )

    response = await client.get("/api/v1/categories?include_system=false")
    assert response.status_code == 200
    data = response.json()
    assert all(item["is_system"] is False for item in data)


@pytest.mark.asyncio
async def test_update_category(authenticated_client):
    client, _ = authenticated_client

    create_response = await client.post(
        "/api/v1/categories",
        json={
            "name": "Old Category",
            "category_type": "expense",
            "icon": "tag",
            "color": "#123456",
        },
    )
    category_id = create_response.json()["id"]

    response = await client.patch(
        f"/api/v1/categories/{category_id}",
        json={"name": "New Category"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "New Category"


@pytest.mark.asyncio
async def test_delete_category(authenticated_client):
    client, _ = authenticated_client

    create_response = await client.post(
        "/api/v1/categories",
        json={
            "name": "Delete Category",
            "category_type": "expense",
            "icon": "tag",
            "color": "#654321",
        },
    )
    category_id = create_response.json()["id"]

    response = await client.delete(f"/api/v1/categories/{category_id}")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_update_system_category_forbidden(authenticated_client):
    client, _ = authenticated_client

    get_response = await client.get("/api/v1/categories")
    categories = get_response.json()
    system_category = next((c for c in categories if c["is_system"] is True), None)
    if not system_category:
        pytest.skip("Системные категории не инициализированы в тестовой БД")

    response = await client.patch(
        f"/api/v1/categories/{system_category['id']}",
        json={"name": "Hacked"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_system_category_forbidden(authenticated_client):
    client, _ = authenticated_client

    get_response = await client.get("/api/v1/categories")
    categories = get_response.json()
    system_category = next((c for c in categories if c["is_system"] is True), None)
    if not system_category:
        pytest.skip("Системные категории не инициализированы в тестовой БД")

    response = await client.delete(f"/api/v1/categories/{system_category['id']}")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_category_unauthorized(authenticated_client):
    client, _ = authenticated_client
    client.headers.pop("Authorization", None)

    response = await client.get("/api/v1/categories")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_category_validation_error(authenticated_client):
    client, _ = authenticated_client

    response = await client.post(
        "/api/v1/categories",
        json={"name": "Broken"},
    )
    assert response.status_code == 422

