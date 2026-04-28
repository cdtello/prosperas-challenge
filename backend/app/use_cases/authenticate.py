from fastapi import HTTPException, status

from app.domain.entities.user import User
from app.domain.ports.user_repository import IUserRepository
from app.infrastructure.auth import create_access_token, hash_password, verify_password


class RegisterUseCase:
    def __init__(self, user_repo: IUserRepository) -> None:
        self._user_repo = user_repo

    async def execute(self, username: str, email: str, password: str) -> str:
        existing = await self._user_repo.get_by_username(username)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken",
            )

        user = User(username=username, email=email, hashed_password=hash_password(password))
        user = await self._user_repo.create(user)
        return create_access_token(user.id)


class LoginUseCase:
    def __init__(self, user_repo: IUserRepository) -> None:
        self._user_repo = user_repo

    async def execute(self, username: str, password: str) -> str:
        user = await self._user_repo.get_by_username(username)
        if user is None or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        return create_access_token(user.id)
