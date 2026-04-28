from unittest.mock import AsyncMock

import pytest

from app.domain.entities.job import Job
from app.domain.value_objects.job_status import JobStatus
from app.use_cases.create_job import CreateJobUseCase


@pytest.fixture
def job_repo():
    repo = AsyncMock()
    repo.create.side_effect = lambda job: job
    return repo


@pytest.fixture
def queue():
    return AsyncMock()


@pytest.mark.asyncio
async def test_create_job_returns_pending_job(job_repo, queue):
    use_case = CreateJobUseCase(job_repo, queue)
    job = await use_case.execute("user-1", "sales_summary", "2024-01", "json")

    assert isinstance(job, Job)
    assert job.status == JobStatus.PENDING
    assert job.user_id == "user-1"
    assert job.report_type == "sales_summary"


@pytest.mark.asyncio
async def test_create_job_publishes_to_queue(job_repo, queue):
    use_case = CreateJobUseCase(job_repo, queue)
    job = await use_case.execute("user-1", "sales_summary", "2024-01", "json")

    queue.publish.assert_called_once_with(job.id)


@pytest.mark.asyncio
async def test_create_job_persists_via_repo(job_repo, queue):
    use_case = CreateJobUseCase(job_repo, queue)
    await use_case.execute("user-1", "sales_summary", "2024-01", "json")

    job_repo.create.assert_called_once()
    created_job = job_repo.create.call_args[0][0]
    assert created_job.user_id == "user-1"


@pytest.mark.asyncio
async def test_create_job_fails_if_queue_raises(job_repo, queue):
    queue.publish.side_effect = Exception("SQS unavailable")
    use_case = CreateJobUseCase(job_repo, queue)

    with pytest.raises(Exception, match="SQS unavailable"):
        await use_case.execute("user-1", "sales_summary", "2024-01", "json")
