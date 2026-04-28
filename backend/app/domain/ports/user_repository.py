from typing import Protocol

from app.domain.entities.user import User


class IUserRepository(Protocol):
    async def get_by_username(self, username: str) -> User | None: ...

    async def create(self, user: User) -> User: ...
