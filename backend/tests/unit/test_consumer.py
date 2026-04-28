import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.worker.consumer import _handle_message, poll_and_process


def _make_message(job_id: str = "job-123", receipt: str = "receipt-abc") -> dict:
    return {"Body": json.dumps({"job_id": job_id}), "ReceiptHandle": receipt}


@pytest.mark.asyncio
async def test_handle_message_calls_use_case():
    message = _make_message()
    mock_use_case = AsyncMock()

    with (
        patch("app.worker.consumer.SqlJobRepository"),
        patch("app.worker.consumer.S3FileStorage"),
        patch("app.worker.consumer.SqsMessageQueue"),
        patch("app.worker.consumer.ProcessJobUseCase", return_value=mock_use_case),
        patch("app.worker.consumer.AsyncSessionLocal") as mock_session,
    ):
        mock_db = AsyncMock()
        mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_db)
        mock_session.return_value.__aexit__ = AsyncMock(return_value=False)

        await _handle_message(message)

    mock_use_case.execute.assert_called_once_with("job-123", "receipt-abc")


@pytest.mark.asyncio
async def test_handle_message_propagates_exception():
    message = _make_message()
    mock_use_case = AsyncMock()
    mock_use_case.execute.side_effect = RuntimeError("processing failed")

    with (
        patch("app.worker.consumer.SqlJobRepository"),
        patch("app.worker.consumer.S3FileStorage"),
        patch("app.worker.consumer.SqsMessageQueue"),
        patch("app.worker.consumer.ProcessJobUseCase", return_value=mock_use_case),
        patch("app.worker.consumer.AsyncSessionLocal") as mock_session,
    ):
        mock_db = AsyncMock()
        mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_db)
        mock_session.return_value.__aexit__ = AsyncMock(return_value=False)

        with pytest.raises(RuntimeError, match="processing failed"):
            await _handle_message(message)


@pytest.mark.asyncio
async def test_poll_and_process_handles_empty_queue():
    mock_queue = AsyncMock()
    mock_queue.receive.side_effect = [[], Exception("stop")]

    with patch("app.worker.consumer.SqsMessageQueue", return_value=mock_queue):
        with pytest.raises(Exception, match="stop"):
            await poll_and_process()

    mock_queue.receive.assert_called()


@pytest.mark.asyncio
async def test_poll_and_process_dispatches_messages():
    messages = [_make_message("job-1", "r-1"), _make_message("job-2", "r-2")]

    call_count = 0

    async def fake_receive(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return messages
        raise StopAsyncIteration("done")

    mock_queue = AsyncMock()
    mock_queue.receive.side_effect = fake_receive

    with (
        patch("app.worker.consumer.SqsMessageQueue", return_value=mock_queue),
        patch("app.worker.consumer._handle_message", new_callable=AsyncMock) as mock_handle,
    ):
        with pytest.raises(StopAsyncIteration):
            await poll_and_process()

    assert mock_handle.call_count == 2


@pytest.mark.asyncio
async def test_poll_and_process_logs_failed_message(caplog):
    messages = [_make_message()]
    call_count = 0

    async def fake_receive(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return messages
        raise StopAsyncIteration("done")

    mock_queue = AsyncMock()
    mock_queue.receive.side_effect = fake_receive

    with (
        patch("app.worker.consumer.SqsMessageQueue", return_value=mock_queue),
        patch(
            "app.worker.consumer._handle_message",
            new_callable=AsyncMock,
            side_effect=RuntimeError("boom"),
        ),
    ):
        with pytest.raises(StopAsyncIteration):
            await poll_and_process()
