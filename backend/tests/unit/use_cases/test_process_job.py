from unittest.mock import AsyncMock, patch

import pytest

from app.domain.entities.job import Job
from app.domain.value_objects.job_status import JobStatus
from app.use_cases.process_job import ProcessJobUseCase


@pytest.fixture
def job_repo():
    repo = AsyncMock()
    job = Job(user_id="u1", report_type="sales", date_range="2024", format="json")
    job.status = JobStatus.PROCESSING
    repo.update_status.return_value = job
    return repo


@pytest.fixture
def storage():
    s = AsyncMock()
    s.upload_report.return_value = "https://s3.example.com/reports/job-1.json"
    return s


@pytest.fixture
def queue():
    return AsyncMock()


@pytest.mark.asyncio
async def test_process_job_happy_path(job_repo, storage, queue):
    with patch("app.use_cases.process_job.asyncio.sleep"):
        await ProcessJobUseCase(job_repo, storage, queue).execute("job-1", "receipt-handle")

    job_repo.update_status.assert_any_call("job-1", JobStatus.PROCESSING)
    storage.upload_report.assert_called_once()
    job_repo.update_status.assert_any_call("job-1", JobStatus.COMPLETED, storage.upload_report.return_value)
    queue.delete.assert_called_once_with("receipt-handle")


@pytest.mark.asyncio
async def test_process_job_not_found_deletes_message(job_repo, storage, queue):
    job_repo.update_status.return_value = None

    await ProcessJobUseCase(job_repo, storage, queue).execute("missing", "receipt-handle")

    queue.delete.assert_called_once_with("receipt-handle")
    storage.upload_report.assert_not_called()


@pytest.mark.asyncio
async def test_process_job_marks_failed_on_error(job_repo, storage, queue):
    storage.upload_report.side_effect = Exception("S3 error")

    with patch("app.use_cases.process_job.asyncio.sleep"):
        with pytest.raises(Exception, match="S3 error"):
            await ProcessJobUseCase(job_repo, storage, queue).execute("job-1", "receipt-handle")

    job_repo.update_status.assert_any_call("job-1", JobStatus.FAILED)
    queue.delete.assert_not_called()
