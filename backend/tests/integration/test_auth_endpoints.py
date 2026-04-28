import pytest


@pytest.mark.asyncio
async def test_health_has_request_id_header(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert "x-request-id" in response.headers


@pytest.mark.asyncio
async def test_register_returns_201_with_token(client):
    response = await client.post(
        "/auth/register",
        json={"username": "alice", "email": "alice@test.com", "password": "secret123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate_returns_409(client):
    payload = {"username": "alice", "email": "alice@test.com", "password": "secret123"}
    await client.post("/auth/register", json=payload)
    response = await client.post("/auth/register", json=payload)

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_returns_token(client):
    await client.post(
        "/auth/register",
        json={"username": "bob", "email": "bob@test.com", "password": "pass123"},
    )
    response = await client.post(
        "/auth/login", json={"username": "bob", "password": "pass123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_wrong_password_returns_401(client):
    await client.post(
        "/auth/register",
        json={"username": "carol", "email": "carol@test.com", "password": "correct"},
    )
    response = await client.post(
        "/auth/login", json={"username": "carol", "password": "wrong"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_health_returns_ok(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
