import asyncio
import json
import logging
import random
from datetime import datetime, timezone

from app.core.db import AsyncSessionLocal
from app.models.job import JobStatus
from app.services import s3_service, sqs_service
from app.services.job_service import update_job_status

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


async def process_message(message: dict) -> None:
    body = json.loads(message["Body"])
    job_id = body["job_id"]
    receipt_handle = message["ReceiptHandle"]

    logger.info("Processing job %s", job_id)

    async with AsyncSessionLocal() as db:
        job = await update_job_status(db, job_id, JobStatus.PROCESSING)
        if job is None:
            logger.warning("Job %s not found, skipping", job_id)
            await sqs_service.delete_message(receipt_handle)
            return

        try:
            sleep_seconds = random.randint(5, 30)
            logger.info("Job %s simulating work for %ds", job_id, sleep_seconds)
            await asyncio.sleep(sleep_seconds)

            report = _generate_dummy_report(job_id, job.report_type)
            result_url = await s3_service.upload_report(job_id, report)

            await update_job_status(db, job_id, JobStatus.COMPLETED, result_url=result_url)
            await sqs_service.delete_message(receipt_handle)
            logger.info("Job %s COMPLETED", job_id)

        except Exception:
            await update_job_status(db, job_id, JobStatus.FAILED)
            logger.exception("Job %s FAILED — message left in SQS for retry/DLQ", job_id)
            raise
