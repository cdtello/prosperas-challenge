import asyncio
import logging
import random
from datetime import datetime, timezone

from app.domain.ports.file_storage import IFileStorage
from app.domain.ports.job_repository import IJobRepository
from app.domain.ports.message_queue import IMessageQueue
from app.domain.value_objects.job_status import JobStatus

logger = logging.getLogger(__name__)


def _generate_dummy_report(job_id: str, report_type: str) -> dict:
    return {
        "job_id": job_id,
        "report_type": report_type,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "rows": random.randint(100, 10000),
        "summary": {
            "total_revenue": round(random.uniform(10000, 999999), 2),
            "total_users": random.randint(500, 50000),
            "conversion_rate": round(random.uniform(0.01, 0.35), 4),
        },
    }


class ProcessJobUseCase:
    def __init__(
        self,
        job_repo: IJobRepository,
        storage: IFileStorage,
        queue: IMessageQueue,
    ) -> None:
        self._job_repo = job_repo
        self._storage = storage
        self._queue = queue

    async def execute(self, job_id: str, receipt_handle: str) -> None:
        logger.info("Processing job %s", job_id)

        job = await self._job_repo.update_status(job_id, JobStatus.PROCESSING)
        if job is None:
            logger.warning("Job %s not found — deleting message", job_id)
            await self._queue.delete(receipt_handle)
            return

        try:
            sleep_seconds = random.randint(5, 30)
            logger.info("Job %s simulating work for %ds", job_id, sleep_seconds)
            await asyncio.sleep(sleep_seconds)

            report = _generate_dummy_report(job_id, job.report_type)
            result_url = await self._storage.upload_report(job_id, report)

            await self._job_repo.update_status(job_id, JobStatus.COMPLETED, result_url)
            await self._queue.delete(receipt_handle)
            logger.info("Job %s COMPLETED", job_id)

        except Exception:
            await self._job_repo.update_status(job_id, JobStatus.FAILED)
            logger.exception("Job %s FAILED — SQS will retry up to maxReceiveCount → DLQ", job_id)
            raise
