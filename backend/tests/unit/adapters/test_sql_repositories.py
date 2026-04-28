import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.adapters.outbound.persistence.models import JobModel, UserModel  # noqa: F401
from app.adapters.outbound.persistence.sql_job_repository import SqlJobRepository
from app.adapters.outbound.persistence.sql_user_repository import SqlUserRepository
from app.domain.entities.job import Job
from app.domain.entities.user import User
from app.domain.value_objects.job_status import JobStatus
from app.infrastructure.db import Base

_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
_Session = async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(autouse=True)
async def reset_db():
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db():
    async with _Session() as session:
        yield session


@pytest_asyncio.fixture
async def job_repo(db):
    return SqlJobRepository(db)


@pytest_asyncio.fixture
async def user_repo(db):
    return SqlUserRepository(db)


# ── SqlJobRepository ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_job_repo_create_and_retrieve(job_repo):
    job = Job(user_id="u1", report_type="sales", date_range="2024", format="json")
    saved = await job_repo.create(job)

    assert saved.id == job.id
    assert saved.status == JobStatus.PENDING
    assert saved.user_id == "u1"


@pytest.mark.asyncio
async def test_job_repo_get_by_id_found(job_repo):
    job = await job_repo.create(
        Job(user_id="u1", report_type="sales", date_range="2024", format="json")
    )
    found = await job_repo.get_by_id(job.id, "u1")

    assert found is not None
    assert found.id == job.id


@pytest.mark.asyncio
async def test_job_repo_get_by_id_not_found(job_repo):
    result = await job_repo.get_by_id("non-existent", "u1")
    assert result is None


@pytest.mark.asyncio
async def test_job_repo_get_by_id_wrong_user(job_repo):
    job = await job_repo.create(
        Job(user_id="u1", report_type="sales", date_range="2024", format="json")
    )
    result = await job_repo.get_by_id(job.id, "u2")
    assert result is None


@pytest.mark.asyncio
async def test_job_repo_list_by_user_paginates(job_repo):
    for _ in range(5):
        await job_repo.create(
            Job(user_id="u1", report_type="sales", date_range="2024", format="json")
        )
    await job_repo.create(
        Job(user_id="u2", report_type="sales", date_range="2024", format="json")
    )

    jobs, total = await job_repo.list_by_user("u1", page=1, size=3)
    assert len(jobs) == 3
    assert total == 5


@pytest.mark.asyncio
async def test_job_repo_list_by_user_page_2(job_repo):
    for _ in range(5):
        await job_repo.create(
            Job(user_id="u1", report_type="sales", date_range="2024", format="json")
        )

    jobs, total = await job_repo.list_by_user("u1", page=2, size=3)
    assert len(jobs) == 2
    assert total == 5


@pytest.mark.asyncio
async def test_job_repo_update_status_to_processing(job_repo):
    job = await job_repo.create(
        Job(user_id="u1", report_type="sales", date_range="2024", format="json")
    )
    updated = await job_repo.update_status(job.id, JobStatus.PROCESSING)

    assert updated is not None
    assert updated.status == JobStatus.PROCESSING


@pytest.mark.asyncio
async def test_job_repo_update_status_to_completed_with_url(job_repo):
    job = await job_repo.create(
        Job(user_id="u1", report_type="sales", date_range="2024", format="json")
    )
    url = "https://s3.amazonaws.com/bucket/report.json"
    updated = await job_repo.update_status(job.id, JobStatus.COMPLETED, result_url=url)

    assert updated.status == JobStatus.COMPLETED
    assert updated.result_url == url


@pytest.mark.asyncio
async def test_job_repo_update_status_to_failed(job_repo):
    job = await job_repo.create(
        Job(user_id="u1", report_type="sales", date_range="2024", format="json")
    )
    updated = await job_repo.update_status(job.id, JobStatus.FAILED)

    assert updated.status == JobStatus.FAILED
    assert updated.result_url is None


@pytest.mark.asyncio
async def test_job_repo_update_status_not_found(job_repo):
    result = await job_repo.update_status("non-existent", JobStatus.PROCESSING)
    assert result is None


# ── SqlUserRepository ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_user_repo_create_and_retrieve(user_repo):
    user = User(username="alice", email="alice@test.com", hashed_password="hashed")
    saved = await user_repo.create(user)

    assert saved.id == user.id
    assert saved.username == "alice"


@pytest.mark.asyncio
async def test_user_repo_get_by_username_found(user_repo):
    await user_repo.create(
        User(username="bob", email="bob@test.com", hashed_password="hashed")
    )
    found = await user_repo.get_by_username("bob")

    assert found is not None
    assert found.username == "bob"


@pytest.mark.asyncio
async def test_user_repo_get_by_username_not_found(user_repo):
    result = await user_repo.get_by_username("unknown")
    assert result is None
