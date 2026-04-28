import asyncio
import logging

from app.core.config import settings
from app.services import sqs_service
from app.worker.processor import process_message

logger = logging.getLogger(__name__)

_semaphore = asyncio.Semaphore(settings.WORKER_CONCURRENCY)


async def _process_with_semaphore(message: dict) -> None:
    async with _semaphore:
        await process_message(message)


async def poll_and_process() -> None:
    logger.info("Worker started — polling SQS with concurrency=%d", settings.WORKER_CONCURRENCY)
    while True:
        messages = await sqs_service.receive_messages(max_messages=settings.SQS_MAX_MESSAGES)

        if not messages:
            await asyncio.sleep(1)
            continue

        logger.info("Received %d message(s) — dispatching concurrently", len(messages))
        tasks = [_process_with_semaphore(msg) for msg in messages]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error("Message %d failed: %s", i, result)
