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
    status = Column(String, nullable=False, default="SUCCEEDED")
    execution_time_ms = Column(Float, default=0.0)
    row_count = Column(Integer, default=0)
    data_quality_score = Column(Float, default=1.0)
    llm_tokens = Column(Integer, default=0)
    estimated_cost_usd = Column(Float, default=0.0)
    provenance_data = Column(JSON, default=dict)
    insights = Column(JSON, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
