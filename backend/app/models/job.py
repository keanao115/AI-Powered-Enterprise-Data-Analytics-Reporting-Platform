from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, Integer, String

from app.core.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, index=True, nullable=False)
    user_id = Column(String, index=True, nullable=False)
    job_type = Column(
        String, nullable=False
    )  # QUERY_PIPELINE, SANDBOX_ANALYSIS, REPORT_GENERATION, EVALUATION
    status = Column(
        String, nullable=False, default="QUEUED"
    )  # QUEUED, RUNNING, SUCCEEDED, FAILED, CANCELLED
    progress_percentage = Column(Integer, default=0)
    current_step = Column(String, default="INITIALIZING")
    result_data = Column(JSON, default=dict)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
