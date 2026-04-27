from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.db import get_db
from app.models.job import JobStatus
from app.models.user import User
from app.services import job_service, sqs_service

router = APIRouter(prefix="/jobs", tags=["jobs"])


class CreateJobRequest(BaseModel):
    report_type: str
    date_range: str
    format: str


class JobResponse(BaseModel):
    job_id: str
    user_id: str
    status: JobStatus
    report_type: str
    date_range: str
    format: str
    created_at: str
    updated_at: str
    result_url: str | None

    model_config = {"from_attributes": True}


class PaginatedJobsResponse(BaseModel):
    items: list[JobResponse]
    total: int
    page: int
    page_size: int


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    body: CreateJobRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JobResponse:
    job = await job_service.create_job(
        db,
        user_id=current_user.id,
        report_type=body.report_type,
        date_range=body.date_range,
        format=body.format,
    )
    await sqs_service.publish_job(job.id)
    return _to_response(job)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JobResponse:
    job = await job_service.get_job_by_id(db, job_id=job_id, user_id=current_user.id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return _to_response(job)


@router.get("", response_model=PaginatedJobsResponse)
async def list_jobs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedJobsResponse:
    jobs, total = await job_service.list_jobs(db, user_id=current_user.id, page=page, page_size=page_size)
    return PaginatedJobsResponse(
        items=[_to_response(j) for j in jobs],
        total=total,
        page=page,
        page_size=page_size,
    )


def _to_response(job) -> JobResponse:
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
