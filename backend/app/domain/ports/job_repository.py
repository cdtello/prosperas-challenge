from typing import Protocol

from app.domain.entities.job import Job
from app.domain.value_objects.job_status import JobStatus


class IJobRepository(Protocol):
    async def create(self, job: Job) -> Job: ...

    async def get_by_id(self, job_id: str, user_id: str) -> Job | None: ...

    async def list_by_user(
        self, user_id: str, page: int, size: int
    ) -> tuple[list[Job], int]: ...

    async def update_status(
        self,
        job_id: str,
        status: JobStatus,
        result_url: str | None = None,
    ) -> Job | None: ...
