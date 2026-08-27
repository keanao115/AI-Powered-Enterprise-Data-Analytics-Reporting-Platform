from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, JSON, Float, Integer
from app.core.database import Base


class QueryHistory(Base):
    __tablename__ = "query_history"

    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, index=True, nullable=False)
    workspace_id = Column(String, index=True, nullable=False)
    user_id = Column(String, index=True, nullable=False)
    question = Column(String, nullable=False)
    generated_sql = Column(String, nullable=True)
    rewritten_sql = Column(String, nullable=True)
    status = Column(String, nullable=False, default="SUCCEEDED")  # SUCCEEDED, BLOCKED, FAILED, CLARIFICATION_REQUIRED
    execution_time_ms = Column(Float, default=0.0)
    row_count = Column(Integer, default=0)
    data_quality_score = Column(Float, default=1.0)
    llm_tokens = Column(Integer, default=0)
    estimated_cost_usd = Column(Float, default=0.0)
    provenance_data = Column(JSON, default=dict)
    insights = Column(JSON, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Report(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, index=True, nullable=False)
    workspace_id = Column(String, index=True, nullable=False)
    user_id = Column(String, index=True, nullable=False)
    query_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    format = Column(String, nullable=False)  # pdf, excel, csv
    file_path = Column(String, nullable=False)
    file_size_bytes = Column(Integer, default=0)
    signed_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, index=True, nullable=False)
    user_id = Column(String, index=True, nullable=False)
    request_id = Column(String, nullable=False, index=True)
    action = Column(String, nullable=False)  # LOGIN, QUERY_EXECUTED, SQL_BLOCKED, PROMPT_INJECTION_BLOCKED, etc.
    resource = Column(String, nullable=False)
    result = Column(String, nullable=False)  # ALLOWED, DENIED, ERROR
    risk_level = Column(String, default="LOW")  # LOW, MEDIUM, HIGH, CRITICAL
    reason = Column(String, nullable=True)
    details = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class AIBudget(Base):
    __tablename__ = "ai_budgets"

    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, unique=True, index=True, nullable=False)
    daily_budget_usd = Column(Float, default=50.0)
    current_daily_spend_usd = Column(Float, default=0.0)
    monthly_budget_usd = Column(Float, default=1000.0)
    current_monthly_spend_usd = Column(Float, default=0.0)
    last_reset_date = Column(String, nullable=False)


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, index=True, nullable=False)
    user_id = Column(String, index=True, nullable=False)
    job_type = Column(String, nullable=False)  # QUERY_PIPELINE, SANDBOX_ANALYSIS, REPORT_GENERATION, EVALUATION
    status = Column(String, nullable=False, default="QUEUED")  # QUEUED, RUNNING, SUCCEEDED, FAILED, CANCELLED
    progress_percentage = Column(Integer, default=0)
    current_step = Column(String, default="INITIALIZING")
    result_data = Column(JSON, default=dict)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
