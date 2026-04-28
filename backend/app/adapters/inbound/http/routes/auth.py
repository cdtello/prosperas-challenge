from fastapi import APIRouter, Depends, status

from app.adapters.inbound.http.dependencies import get_user_repository
from app.adapters.inbound.http.schemas import LoginRequest, RegisterRequest, TokenResponse
from app.adapters.outbound.persistence.sql_user_repository import SqlUserRepository
from app.use_cases.authenticate import LoginUseCase, RegisterUseCase

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    user_repo: SqlUserRepository = Depends(get_user_repository),
) -> TokenResponse:
    token = await RegisterUseCase(user_repo).execute(body.username, body.email, body.password)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    user_repo: SqlUserRepository = Depends(get_user_repository),
) -> TokenResponse:
    token = await LoginUseCase(user_repo).execute(body.username, body.password)
    return TokenResponse(access_token=token)
