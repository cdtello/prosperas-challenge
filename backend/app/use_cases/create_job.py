from app.domain.entities.job import Job
from app.domain.ports.job_repository import IJobRepository
from app.domain.ports.message_queue import IMessageQueue


class CreateJobUseCase:
    def __init__(self, job_repo: IJobRepository, queue: IMessageQueue) -> None:
        self._job_repo = job_repo
        self._queue = queue

    async def execute(self, user_id: str, report_type: str, date_range: str, format: str) -> Job:
        job = Job(user_id=user_id, report_type=report_type, date_range=date_range, format=format)
        job = await self._job_repo.create(job)
        await self._queue.publish(job.id)
        return job
