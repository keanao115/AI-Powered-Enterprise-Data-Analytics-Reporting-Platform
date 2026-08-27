import duckdb
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.core.config import settings

Base = declarative_base()

# Application Database Engine
engine_kwargs = {}
if settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    **engine_kwargs
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


import os

def get_analytics_db_path() -> str:
    """Returns absolute path to the active DuckDB analytics database."""
    if "ANALYTICS_DB_PATH" in os.environ and os.environ["ANALYTICS_DB_PATH"]:
        return os.path.abspath(os.environ["ANALYTICS_DB_PATH"])
    
    url = getattr(settings, "ANALYTICS_DATABASE_URL", "duckdb:///./analytics_demo.duckdb")
    clean_name = url.replace("duckdb:///", "").lstrip("./")
    
    candidates = [
        os.path.abspath(clean_name),
        os.path.abspath(os.path.join(os.getcwd(), clean_name)),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../../", clean_name)),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../", clean_name)),
    ]
    for cand in candidates:
        if os.path.exists(cand):
            return cand
    return candidates[0]


class AnalyticsDatabaseAdapter:
    """
    Adapter for executing read-only analytics queries against DuckDB or PostgreSQL.
    """

    def __init__(self, db_url: str = settings.ANALYTICS_DATABASE_URL):
        self.db_url = db_url

    def execute_query(self, sql_query: str, params: dict = None) -> dict:
        """
        Executes a read-only SQL query and returns column names and rows.
        """
        if self.db_url.startswith("duckdb"):
            db_path = get_analytics_db_path()
            conn = duckdb.connect(db_path, read_only=True)
            try:
                if params:
                    rel = conn.execute(sql_query, params)
                else:
                    rel = conn.execute(sql_query)
                columns = [desc[0] for desc in rel.description] if rel.description else []
                rows = rel.fetchall()
                # Convert non-serializable objects (dates/decimals) to strings
                clean_rows = []
                for row in rows:
                    clean_rows.append([str(val) if val is not None else None for val in row])
                return {
                    "columns": columns,
                    "rows": clean_rows,
                    "row_count": len(clean_rows),
                }
            finally:
                conn.close()
        else:
            # PostgreSQL Analytics fallback
            import psycopg2

            conn = psycopg2.connect(self.db_url)
            conn.set_session(readonly=True)
            cursor = conn.cursor()
            try:
                cursor.execute(sql_query, params or {})
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                rows = cursor.fetchall()
                clean_rows = []
                for row in rows:
                    clean_rows.append([str(val) if val is not None else None for val in row])
                return {
                    "columns": columns,
                    "rows": clean_rows,
                    "row_count": len(clean_rows),
                }
            finally:
                cursor.close()
                conn.close()


analytics_adapter = AnalyticsDatabaseAdapter()
