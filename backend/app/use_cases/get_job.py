from app.domain.entities.job import Job
from app.domain.ports.job_repository import IJobRepository


class GetJobUseCase:
    def __init__(self, job_repo: IJobRepository) -> None:
        self._job_repo = job_repo

    async def execute(self, job_id: str, user_id: str) -> Job | None:
        return await self._job_repo.get_by_id(job_id, user_id)
