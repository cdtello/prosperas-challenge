import pytest
from fastapi import FastAPI, HTTPException
from httpx import ASGITransport, AsyncClient

from app.infrastructure.errors import register_error_handlers
from app.infrastructure.middleware import RequestContextMiddleware


def _build_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(RequestContextMiddleware)
    register_error_handlers(app)

    @app.get("/ok")
    async def ok():
        return {"status": "ok"}

    @app.get("/http-error")
    async def http_error():
        raise HTTPException(status_code=404, detail="not found")

    return app


@pytest.fixture
def test_app():
    return _build_app()


@pytest.mark.asyncio
async def test_request_id_header_present(test_app):
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        response = await client.get("/ok")
    assert "x-request-id" in response.headers
    assert len(response.headers["x-request-id"]) == 36


@pytest.mark.asyncio
async def test_http_exception_returns_correct_status(test_app):
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        response = await client.get("/http-error")
    assert response.status_code == 404
    body = response.json()
    assert body["detail"] == "not found"
    assert "request_id" in body


@pytest.mark.asyncio
async def test_request_id_is_uuid_format(test_app):
    import re
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        r1 = await client.get("/ok")
        r2 = await client.get("/ok")
    uuid_pattern = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    assert uuid_pattern.match(r1.headers["x-request-id"])
    assert r1.headers["x-request-id"] != r2.headers["x-request-id"]
