from unittest.mock import AsyncMock, patch

import pytest


async def _register_and_login(client) -> str:
    await client.post(
        "/auth/register",
        json={"username": "testuser", "email": "test@test.com", "password": "secret123"},
    )
    resp = await client.post("/auth/login", json={"username": "testuser", "password": "secret123"})
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_create_job_returns_pending(client):
    token = await _register_and_login(client)

    with patch("app.adapters.outbound.queue.sqs_queue.SqsMessageQueue.publish", new_callable=AsyncMock):
        response = await client.post(
            "/jobs",
            json={"report_type": "sales_summary", "date_range": "2024-01", "format": "json"},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "PENDING"
    assert data["report_type"] == "sales_summary"
    assert "job_id" in data


@pytest.mark.asyncio
async def test_get_job_returns_job(client):
    token = await _register_and_login(client)

    with patch("app.adapters.outbound.queue.sqs_queue.SqsMessageQueue.publish", new_callable=AsyncMock):
        create_resp = await client.post(
            "/jobs",
            json={"report_type": "sales_summary", "date_range": "2024-01", "format": "json"},
            headers={"Authorization": f"Bearer {token}"},
        )
    job_id = create_resp.json()["job_id"]

    response = await client.get(f"/jobs/{job_id}", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["job_id"] == job_id


@pytest.mark.asyncio
async def test_get_job_not_found_returns_404(client):
    token = await _register_and_login(client)
    response = await client.get("/jobs/non-existent", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_jobs_returns_paginated(client):
    token = await _register_and_login(client)

    with patch("app.adapters.outbound.queue.sqs_queue.SqsMessageQueue.publish", new_callable=AsyncMock):
        for _ in range(3):
            await client.post(
                "/jobs",
                json={"report_type": "sales", "date_range": "2024", "format": "json"},
                headers={"Authorization": f"Bearer {token}"},
            )

    response = await client.get("/jobs", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3


@pytest.mark.asyncio
async def test_create_job_requires_auth(client):
    response = await client.post(
        "/jobs",
        json={"report_type": "sales", "date_range": "2024", "format": "json"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_jobs_isolated_between_users(client):
    for username, email in [("user1", "u1@t.com"), ("user2", "u2@t.com")]:
        await client.post(
            "/auth/register",
            json={"username": username, "email": email, "password": "pass"},
        )

    resp1 = await client.post("/auth/login", json={"username": "user1", "password": "pass"})
    token1 = resp1.json()["access_token"]

    with patch("app.adapters.outbound.queue.sqs_queue.SqsMessageQueue.publish", new_callable=AsyncMock):
        await client.post(
            "/jobs",
            json={"report_type": "sales", "date_range": "2024", "format": "json"},
            headers={"Authorization": f"Bearer {token1}"},
        )

    resp2 = await client.post("/auth/login", json={"username": "user2", "password": "pass"})
    token2 = resp2.json()["access_token"]
    list_resp = await client.get("/jobs", headers={"Authorization": f"Bearer {token2}"})

    assert list_resp.json()["total"] == 0
