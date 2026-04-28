from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.outbound.persistence.sql_job_repository import SqlJobRepository
from app.adapters.outbound.persistence.sql_user_repository import SqlUserRepository
from app.adapters.outbound.queue.sqs_queue import SqsMessageQueue
from app.adapters.outbound.storage.s3_storage import S3FileStorage
from app.infrastructure.auth import decode_access_token
from app.infrastructure.db import get_db

bearer_scheme = HTTPBearer()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    try:
        return decode_access_token(credentials.credentials)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc


def get_job_repository(db: AsyncSession = Depends(get_db)) -> SqlJobRepository:
    return SqlJobRepository(db)


def get_user_repository(db: AsyncSession = Depends(get_db)) -> SqlUserRepository:
    return SqlUserRepository(db)


def get_message_queue() -> SqsMessageQueue:
    return SqsMessageQueue()


def get_file_storage() -> S3FileStorage:
    return S3FileStorage()
