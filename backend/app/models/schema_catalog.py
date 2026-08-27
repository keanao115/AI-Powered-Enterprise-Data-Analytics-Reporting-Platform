from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, JSON
from app.core.database import Base


class SchemaCatalog(Base):
    __tablename__ = "schema_catalog"

    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, index=True, nullable=False)
    workspace_id = Column(String, index=True, nullable=False)
    table_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    columns_metadata = Column(JSON, default=list)  # list of column dicts with sensitivity classification
    row_count_estimate = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
