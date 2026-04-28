from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from app.domain.value_objects.job_status import JobStatus


@dataclass
class Job:
    user_id: str
    report_type: str
    date_range: str
    format: str
    id: str = field(default_factory=lambda: str(uuid4()))
    status: JobStatus = field(default=JobStatus.PENDING)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    result_url: str | None = None
