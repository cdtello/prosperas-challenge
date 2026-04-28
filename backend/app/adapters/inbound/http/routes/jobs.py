from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.adapters.inbound.http.dependencies import (
    get_current_user_id,
    get_job_repository,
    get_message_queue,
)
from app.adapters.inbound.http.schemas import (
    CreateJobRequest,
    JobResponse,
    PaginatedJobsResponse,
)
from app.adapters.outbound.persistence.sql_job_repository import SqlJobRepository
from app.adapters.outbound.queue.sqs_queue import SqsMessageQueue
from app.domain.entities.job import Job
from app.use_cases.create_job import CreateJobUseCase
from app.use_cases.get_job import GetJobUseCase
from app.use_cases.list_jobs import ListJobsUseCase

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _to_response(job: Job) -> JobResponse:
    return JobResponse(
        job_id=job.id,
        user_id=job.user_id,
        status=job.status,
        report_type=job.report_type,
        date_range=job.date_range,
        format=job.format,
        created_at=job.created_at.isoformat(),
        updated_at=job.updated_at.isoformat(),
        result_url=job.result_url,
    )


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    body: CreateJobRequest,
    user_id: str = Depends(get_current_user_id),
    job_repo: SqlJobRepository = Depends(get_job_repository),
    queue: SqsMessageQueue = Depends(get_message_queue),
) -> JobResponse:
    job = await CreateJobUseCase(job_repo, queue).execute(
        user_id, body.report_type, body.date_range, body.format
    )
    return _to_response(job)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    user_id: str = Depends(get_current_user_id),
    job_repo: SqlJobRepository = Depends(get_job_repository),
) -> JobResponse:
    job = await GetJobUseCase(job_repo).execute(job_id, user_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return _to_response(job)


@router.get("", response_model=PaginatedJobsResponse)
async def list_jobs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
    job_repo: SqlJobRepository = Depends(get_job_repository),
) -> PaginatedJobsResponse:
    jobs, total = await ListJobsUseCase(job_repo).execute(user_id, page, page_size)
    return PaginatedJobsResponse(
        items=[_to_response(j) for j in jobs],
        total=total,
        page=page,
        page_size=page_size,
    )
