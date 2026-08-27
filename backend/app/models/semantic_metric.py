from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, JSON, Boolean
from app.core.database import Base


class DataSource(Base):
    __tablename__ = "data_sources"

    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, index=True, nullable=False)
    workspace_id = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)
    engine = Column(String, nullable=False)  # duckdb, postgresql
    connection_url = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


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


class SemanticMetric(Base):
    __tablename__ = "semantic_metrics"

    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, index=True, nullable=False)
    workspace_id = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)
    aliases = Column(JSON, default=list)
    description = Column(String, nullable=False)
    sql_expression = Column(String, nullable=False)
    base_table = Column(String, nullable=False)
    default_filters = Column(JSON, default=list)
    allowed_dimensions = Column(JSON, default=list)
    sensitivity = Column(String, default="INTERNAL")
    version = Column(String, default="1.0.0")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
