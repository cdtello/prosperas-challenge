from app.domain.entities.job import Job
from app.domain.ports.job_repository import IJobRepository


class ListJobsUseCase:
    def __init__(self, job_repo: IJobRepository) -> None:
        self._job_repo = job_repo

    async def execute(self, user_id: str, page: int, size: int) -> tuple[list[Job], int]:
        return await self._job_repo.list_by_user(user_id, page, size)
