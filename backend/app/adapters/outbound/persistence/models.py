from datetime import datetime

from sqlalchemy import DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db import Base


class JobModel(Base):
    __tablename__ = "jobs"
    __table_args__ = (Index("ix_jobs_user_id", "user_id"),)

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    report_type: Mapped[str] = mapped_column(String(100), nullable=False)
    date_range: Mapped[str] = mapped_column(String(100), nullable=False)
    format: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    result_url: Mapped[str | None] = mapped_column(String, nullable=True)


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
