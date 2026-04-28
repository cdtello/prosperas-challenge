from unittest.mock import AsyncMock

import pytest

from app.domain.entities.job import Job
from app.use_cases.get_job import GetJobUseCase


@pytest.fixture
def job_repo():
    return AsyncMock()


@pytest.mark.asyncio
async def test_get_job_returns_job(job_repo):
    expected = Job(user_id="user-1", report_type="sales", date_range="2024", format="json")
    job_repo.get_by_id.return_value = expected

    result = await GetJobUseCase(job_repo).execute(expected.id, "user-1")

    assert result == expected
    job_repo.get_by_id.assert_called_once_with(expected.id, "user-1")


@pytest.mark.asyncio
async def test_get_job_returns_none_when_not_found(job_repo):
    job_repo.get_by_id.return_value = None

    result = await GetJobUseCase(job_repo).execute("non-existent", "user-1")

    assert result is None


@pytest.mark.asyncio
async def test_get_job_filters_by_user(job_repo):
    job_repo.get_by_id.return_value = None

    await GetJobUseCase(job_repo).execute("job-1", "user-2")

    job_repo.get_by_id.assert_called_once_with("job-1", "user-2")
