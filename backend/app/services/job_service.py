from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job, JobStatus


async def create_job(db: AsyncSession, user_id: str, report_type: str, date_range: str, format: str) -> Job:
    job = Job(user_id=user_id, report_type=report_type, date_range=date_range, format=format)
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


async def get_job_by_id(db: AsyncSession, job_id: str, user_id: str) -> Job | None:
    result = await db.execute(select(Job).where(Job.id == job_id, Job.user_id == user_id))
    return result.scalar_one_or_none()


async def list_jobs(db: AsyncSession, user_id: str, page: int, page_size: int) -> tuple[list[Job], int]:
    offset = (page - 1) * page_size
    result = await db.execute(
        select(Job).where(Job.user_id == user_id).order_by(Job.created_at.desc()).offset(offset).limit(page_size)
    )
    jobs = list(result.scalars().all())

    count_result = await db.execute(select(Job).where(Job.user_id == user_id))
    total = len(list(count_result.scalars().all()))
    return jobs, total


async def update_job_status(
    db: AsyncSession,
    job_id: str,
    status: JobStatus,
    result_url: str | None = None,
) -> Job | None:
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if job is None:
        return None
    job.status = status
    job.updated_at = datetime.now(timezone.utc)
    if result_url is not None:
        job.result_url = result_url
    await db.commit()
    await db.refresh(job)
    return job
