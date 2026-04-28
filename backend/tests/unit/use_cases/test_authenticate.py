from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from app.domain.entities.user import User
from app.infrastructure.auth import hash_password
from app.use_cases.authenticate import LoginUseCase, RegisterUseCase


@pytest.fixture
def user_repo():
    return AsyncMock()


@pytest.fixture
def existing_user():
    return User(
        username="testuser",
        email="test@test.com",
        hashed_password=hash_password("secret123"),
    )


@pytest.mark.asyncio
async def test_register_returns_token(user_repo):
    user_repo.get_by_username.return_value = None
    user_repo.create.side_effect = lambda u: u

    token = await RegisterUseCase(user_repo).execute("newuser", "new@test.com", "secret123")

    assert isinstance(token, str)
    assert len(token) > 0


@pytest.mark.asyncio
async def test_register_raises_conflict_if_username_taken(user_repo, existing_user):
    user_repo.get_by_username.return_value = existing_user

    with pytest.raises(HTTPException) as exc:
        await RegisterUseCase(user_repo).execute("testuser", "other@test.com", "pass")

    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_login_returns_token(user_repo, existing_user):
    user_repo.get_by_username.return_value = existing_user

    token = await LoginUseCase(user_repo).execute("testuser", "secret123")

    assert isinstance(token, str)


@pytest.mark.asyncio
async def test_login_raises_401_with_wrong_password(user_repo, existing_user):
    user_repo.get_by_username.return_value = existing_user

    with pytest.raises(HTTPException) as exc:
        await LoginUseCase(user_repo).execute("testuser", "wrong-password")

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_login_raises_401_when_user_not_found(user_repo):
    user_repo.get_by_username.return_value = None

    with pytest.raises(HTTPException) as exc:
        await LoginUseCase(user_repo).execute("unknown", "any")

    assert exc.value.status_code == 401
