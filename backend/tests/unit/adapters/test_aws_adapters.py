import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.adapters.outbound.queue.sqs_queue import SqsMessageQueue
from app.adapters.outbound.storage.s3_storage import S3FileStorage


def _mock_sqs_client():
    client = AsyncMock()
    ctx = MagicMock()
    ctx.__aenter__ = AsyncMock(return_value=client)
    ctx.__aexit__ = AsyncMock(return_value=False)
    return client, ctx


def _mock_s3_client():
    client = AsyncMock()
    ctx = MagicMock()
    ctx.__aenter__ = AsyncMock(return_value=client)
    ctx.__aexit__ = AsyncMock(return_value=False)
    return client, ctx


# ── SqsMessageQueue ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_sqs_publish_sends_message():
    client, ctx = _mock_sqs_client()
    with patch("app.adapters.outbound.queue.sqs_queue.get_session") as mock_session:
        mock_session.return_value.client.return_value = ctx
        await SqsMessageQueue().publish("job-123")

    client.send_message.assert_called_once()
    body = json.loads(client.send_message.call_args[1]["MessageBody"])
    assert body["job_id"] == "job-123"


@pytest.mark.asyncio
async def test_sqs_receive_returns_messages():
    client, ctx = _mock_sqs_client()
    client.receive_message.return_value = {
        "Messages": [{"Body": '{"job_id":"job-1"}', "ReceiptHandle": "rh-1"}]
    }
    with patch("app.adapters.outbound.queue.sqs_queue.get_session") as mock_session:
        mock_session.return_value.client.return_value = ctx
        messages = await SqsMessageQueue().receive(max_messages=5)

    assert len(messages) == 1
    assert messages[0]["ReceiptHandle"] == "rh-1"


@pytest.mark.asyncio
async def test_sqs_receive_returns_empty_when_no_messages():
    client, ctx = _mock_sqs_client()
    client.receive_message.return_value = {}
    with patch("app.adapters.outbound.queue.sqs_queue.get_session") as mock_session:
        mock_session.return_value.client.return_value = ctx
        messages = await SqsMessageQueue().receive()

    assert messages == []


@pytest.mark.asyncio
async def test_sqs_delete_calls_delete_message():
    client, ctx = _mock_sqs_client()
    with patch("app.adapters.outbound.queue.sqs_queue.get_session") as mock_session:
        mock_session.return_value.client.return_value = ctx
        await SqsMessageQueue().delete("receipt-handle-xyz")

    client.delete_message.assert_called_once()
    assert client.delete_message.call_args[1]["ReceiptHandle"] == "receipt-handle-xyz"


# ── S3FileStorage ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_s3_upload_returns_localstack_url_when_endpoint_set():
    client, ctx = _mock_s3_client()
    with (
        patch("app.adapters.outbound.storage.s3_storage.get_session") as mock_session,
        patch("app.adapters.outbound.storage.s3_storage.settings") as mock_settings,
    ):
        mock_settings.AWS_ENDPOINT_URL = "http://localhost:4566"
        mock_settings.S3_BUCKET_NAME = "test-bucket"
        mock_settings.AWS_DEFAULT_REGION = "us-east-1"
        mock_session.return_value.client.return_value = ctx

        url = await S3FileStorage().upload_report("job-1", {"key": "value"})

    assert "localhost:4566" in url
    assert "job-1" in url
    client.put_object.assert_called_once()


@pytest.mark.asyncio
async def test_s3_upload_returns_aws_url_in_production():
    client, ctx = _mock_s3_client()
    with (
        patch("app.adapters.outbound.storage.s3_storage.get_session") as mock_session,
        patch("app.adapters.outbound.storage.s3_storage.settings") as mock_settings,
    ):
        mock_settings.AWS_ENDPOINT_URL = None
        mock_settings.S3_BUCKET_NAME = "prosperas-reports"
        mock_settings.AWS_DEFAULT_REGION = "us-east-1"
        mock_session.return_value.client.return_value = ctx

        url = await S3FileStorage().upload_report("job-1", {"key": "value"})

    assert "s3.us-east-1.amazonaws.com" in url
    assert "prosperas-reports" in url
