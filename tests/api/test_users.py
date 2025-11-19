import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from app.core.security import get_password_hash


@pytest.mark.anyio
async def test_create_user_success(async_client: AsyncClient):
    response = await async_client.post(
        "/users",
        json={"username": "testuser", "password": "Test@1234"},
    )

    assert response.status_code == 201

    data = response.json()
    assert data["username"] == "testuser"
    assert data["is_active"] is True
    assert data["role"] == "user"
    assert "id" in data
    assert "password" not in data


@pytest.mark.anyio
async def test_create_user_duplicate_username(
    async_client: AsyncClient, db_session: AsyncSession
):
    existing_user = User(
        username="existinguser",
        hashed_password=get_password_hash("Test@1234"),
        is_active=True,
        role=UserRole.USER,
    )
    db_session.add(existing_user)
    await db_session.commit()

    response = await async_client.post(
        "/users",
        json={"username": "existinguser", "password": "AnotherPass!1"},
    )

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Um usuário com este nome de usuário já existe."


@pytest.mark.anyio
@pytest.mark.parametrize(
    "username, password, status_code",
    [
        ("usr", "Test@1234", 422),  # Username muito curto
        ("toolongusername123", "Test@1234", 422),  # Username muito longo
        ("testuser", "short", 422),  # Senha muito curta
        ("testuser", "toolongpassword123456", 422),  # Senha muito longa
        ("invalid user", "Test@1234", 422),  # Username com caracteres inválidos
    ],
)
async def test_create_user_validation_errors(
    async_client: AsyncClient, username: str, password: str, status_code: int
):
    response = await async_client.post(
        "/users",
        json={"username": username, "password": password},
    )

    assert response.status_code == status_code
