from pydantic import BaseModel, EmailStr

from app.domain.value_objects.job_status import JobStatus


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


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
