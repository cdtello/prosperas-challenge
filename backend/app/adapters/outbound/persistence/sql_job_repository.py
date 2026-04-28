from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.outbound.persistence.models import JobModel
from app.domain.entities.job import Job
from app.domain.value_objects.job_status import JobStatus


class SqlJobRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(self, job: Job) -> Job:
        model = self._to_model(job)
        self._db.add(model)
        await self._db.commit()
        await self._db.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, job_id: str, user_id: str) -> Job | None:
        result = await self._db.execute(
            select(JobModel).where(JobModel.id == job_id, JobModel.user_id == user_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_by_user(self, user_id: str, page: int, size: int) -> tuple[list[Job], int]:
        offset = (page - 1) * size
        result = await self._db.execute(
            select(JobModel)
            .where(JobModel.user_id == user_id)
            .order_by(JobModel.created_at.desc())
            .offset(offset)
            .limit(size)
        )
        jobs = [self._to_entity(m) for m in result.scalars().all()]

        count_result = await self._db.execute(
            select(func.count()).select_from(JobModel).where(JobModel.user_id == user_id)
        )
        total = count_result.scalar_one()
        return jobs, total

    async def update_status(
        self, job_id: str, status: JobStatus, result_url: str | None = None
    ) -> Job | None:
        result = await self._db.execute(select(JobModel).where(JobModel.id == job_id))
        model = result.scalar_one_or_none()
        if model is None:
            return None
        model.status = status.value
        model.updated_at = datetime.now(timezone.utc)
        if result_url is not None:
            model.result_url = result_url
        await self._db.commit()
        await self._db.refresh(model)
        return self._to_entity(model)

    def _to_model(self, job: Job) -> JobModel:
        return JobModel(
            id=job.id,
            user_id=job.user_id,
            status=job.status.value,
            report_type=job.report_type,
            date_range=job.date_range,
            format=job.format,
            created_at=job.created_at,
            updated_at=job.updated_at,
            result_url=job.result_url,
        )

    def _to_entity(self, model: JobModel) -> Job:
        return Job(
            id=model.id,
            user_id=model.user_id,
            status=JobStatus(model.status),
            report_type=model.report_type,
            date_range=model.date_range,
            format=model.format,
            created_at=model.created_at,
            updated_at=model.updated_at,
            result_url=model.result_url,
        )
