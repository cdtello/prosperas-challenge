import asyncio
import json
import logging

from app.adapters.outbound.persistence.sql_job_repository import SqlJobRepository
from app.adapters.outbound.queue.sqs_queue import SqsMessageQueue
from app.adapters.outbound.storage.s3_storage import S3FileStorage
from app.infrastructure.config import settings
from app.infrastructure.db import AsyncSessionLocal
from app.use_cases.process_job import ProcessJobUseCase

logger = logging.getLogger(__name__)

_semaphore = asyncio.Semaphore(settings.WORKER_CONCURRENCY)


async def _handle_message(message: dict) -> None:
    async with _semaphore:
        body = json.loads(message["Body"])
        job_id = body["job_id"]
        receipt_handle = message["ReceiptHandle"]

        async with AsyncSessionLocal() as db:
            use_case = ProcessJobUseCase(
                job_repo=SqlJobRepository(db),
                storage=S3FileStorage(),
                queue=SqsMessageQueue(),
            )
            await use_case.execute(job_id, receipt_handle)


async def poll_and_process() -> None:
    queue = SqsMessageQueue()
    logger.info("Worker started — concurrency=%d", settings.WORKER_CONCURRENCY)

    while True:
        messages = await queue.receive(max_messages=settings.SQS_MAX_MESSAGES)

        if not messages:
            await asyncio.sleep(1)
            continue

        logger.info("Received %d message(s)", len(messages))
        tasks = [_handle_message(msg) for msg in messages]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error("Message %d failed: %s", i, result)
