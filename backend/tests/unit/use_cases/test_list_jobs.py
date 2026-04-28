from unittest.mock import AsyncMock

import pytest

from app.domain.entities.job import Job
from app.use_cases.list_jobs import ListJobsUseCase


@pytest.fixture
def job_repo():
    return AsyncMock()


@pytest.mark.asyncio
async def test_list_jobs_returns_paginated_results(job_repo):
    jobs = [Job(user_id="u1", report_type="s", date_range="2024", format="json") for _ in range(3)]
    job_repo.list_by_user.return_value = (jobs, 3)

    result_jobs, total = await ListJobsUseCase(job_repo).execute("u1", page=1, size=20)

    assert len(result_jobs) == 3
    assert total == 3
    job_repo.list_by_user.assert_called_once_with("u1", 1, 20)


@pytest.mark.asyncio
async def test_list_jobs_returns_empty_for_new_user(job_repo):
    job_repo.list_by_user.return_value = ([], 0)

    result_jobs, total = await ListJobsUseCase(job_repo).execute("new-user", page=1, size=20)

    assert result_jobs == []
    assert total == 0
