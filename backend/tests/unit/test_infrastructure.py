import pytest
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError

from app.infrastructure.auth import create_access_token, decode_access_token
from app.infrastructure.aws import client_kwargs
from app.infrastructure.errors import register_error_handlers
from app.infrastructure.middleware import RequestContextMiddleware


# ── auth.py ───────────────────────────────────────────────────────────────────

def test_decode_valid_token_returns_user_id():
    token = create_access_token("user-123")
    user_id = decode_access_token(token)
    assert user_id == "user-123"


def test_decode_invalid_token_raises_value_error():
    with pytest.raises(ValueError, match="Invalid token"):
        decode_access_token("not-a-valid-jwt")


def test_decode_tampered_token_raises_value_error():
    token = create_access_token("user-123")
    tampered = token[:-5] + "XXXXX"
    with pytest.raises(ValueError, match="Invalid token"):
        decode_access_token(tampered)


# ── aws.py ────────────────────────────────────────────────────────────────────

def test_client_kwargs_without_endpoint():
    with pytest.MonkeyPatch().context() as mp:
        mp.setattr("app.infrastructure.aws.settings.AWS_ENDPOINT_URL", None)
        mp.setattr("app.infrastructure.aws.settings.AWS_DEFAULT_REGION", "us-east-1")
        mp.setattr("app.infrastructure.aws.settings.AWS_ACCESS_KEY_ID", "key")
        mp.setattr("app.infrastructure.aws.settings.AWS_SECRET_ACCESS_KEY", "secret")
        kwargs = client_kwargs()

    assert "endpoint_url" not in kwargs
    assert kwargs["region_name"] == "us-east-1"


def test_client_kwargs_with_localstack_endpoint():
    with pytest.MonkeyPatch().context() as mp:
        mp.setattr("app.infrastructure.aws.settings.AWS_ENDPOINT_URL", "http://localhost:4566")
        mp.setattr("app.infrastructure.aws.settings.AWS_DEFAULT_REGION", "us-east-1")
        mp.setattr("app.infrastructure.aws.settings.AWS_ACCESS_KEY_ID", "test")
        mp.setattr("app.infrastructure.aws.settings.AWS_SECRET_ACCESS_KEY", "test")
        kwargs = client_kwargs()

    assert kwargs["endpoint_url"] == "http://localhost:4566"


# ── errors.py — validation paths ──────────────────────────────────────────────

def _build_validation_app() -> FastAPI:
    from pydantic import BaseModel

    app = FastAPI()
    app.add_middleware(RequestContextMiddleware)
    register_error_handlers(app)

    class Body(BaseModel):
        name: str
        age: int

    @app.post("/validated")
    async def validated(body: Body):
        return body

    return app


@pytest.mark.asyncio
async def test_request_validation_error_returns_422():
    app = _build_validation_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/validated", json={"name": "Alice", "age": "not-a-number"})
    assert response.status_code == 422
    body = response.json()
    assert "detail" in body
