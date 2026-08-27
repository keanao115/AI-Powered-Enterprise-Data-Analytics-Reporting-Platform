import os
import csv
from typing import List, Dict, Any, Optional
import duckdb
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import FileResponse, Response

from app.core.security import require_permission
from app.core.permissions import Permission
from app.core.tenant import TenantContext
from app.semantic.dataset_catalog import ENTERPRISE_DATASET_CATALOG, dataset_catalog

router = APIRouter(prefix="/datasets", tags=["Datasets"])

from app.core.config import settings

def get_db_path() -> str:
    if os.path.exists("analytics_demo.duckdb"):
        return os.path.abspath("analytics_demo.duckdb")
    if os.path.exists("backend/analytics_demo.duckdb"):
        return os.path.abspath("backend/analytics_demo.duckdb")
    if hasattr(settings, "ANALYTICS_DATABASE_URL") and settings.ANALYTICS_DATABASE_URL.startswith("duckdb:///"):
        return settings.ANALYTICS_DATABASE_URL.replace("duckdb:///", "")
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../analytics_demo.duckdb"))

RAW_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/raw"))


def _query_curated_table_details(dataset: Dict[str, Any], limit: int = 50, offset: int = 0, search: Optional[str] = None) -> Dict[str, Any]:
    """Queries DuckDB for table structure and profiling statistics."""
    primary_table = dataset["tables"][0]
    
    conn = duckdb.connect(get_db_path())
    try:
        # Check if table exists
        exists = conn.execute(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{primary_table}'").fetchone()[0]
        if not exists:
            # Fallback to demo tables if not yet seeded
            return {
                "metadata": dataset,
                "columns": [],
                "rows": [],
                "total_rows": 0,
                "column_stats": [],
            }

        # Fetch columns
        desc = conn.execute(f"DESCRIBE {primary_table}").fetchall()
        columns = [d[0] for d in desc]

        # Total count
        total_rows = conn.execute(f"SELECT COUNT(*) FROM {primary_table}").fetchone()[0]

        # Search or fetch paginated rows
        if search and search.strip():
            safe_q = search.strip().replace("'", "''")
            where_clauses = [f"CAST({c} AS VARCHAR) ILIKE '%{safe_q}%'" for c in columns]
            where_sql = " OR ".join(where_clauses)
            rows_data = conn.execute(f"SELECT * FROM {primary_table} WHERE {where_sql} LIMIT {limit} OFFSET {offset}").fetchall()
            filtered_count = conn.execute(f"SELECT COUNT(*) FROM {primary_table} WHERE {where_sql}").fetchone()[0]
            total_rows = filtered_count
        else:
            rows_data = conn.execute(f"SELECT * FROM {primary_table} LIMIT {limit} OFFSET {offset}").fetchall()

        dict_rows = [dict(zip(columns, row)) for row in rows_data]

        # Compute column profiling statistics
        stats = []
        for col in columns:
            stats.append({
                "column_name": col,
                "type": next((d[1] for d in desc if d[0] == col), "VARCHAR"),
                "sample_values": [str(r[col]) for r in dict_rows[:3] if col in r and r[col] is not None]
            })

        return {
            "metadata": dataset,
            "columns": columns,
            "rows": dict_rows,
            "total_rows": total_rows,
            "column_stats": stats,
            "tables": dataset.get("tables", [primary_table]),
        }
    finally:
        conn.close()


@router.get("")
async def list_datasets(
    ctx: TenantContext = Depends(require_permission(Permission.DATASOURCE_VIEW))
) -> List[Dict[str, Any]]:
    """List all 6 real-world enterprise datasets with rich provenance metadata."""
    return ENTERPRISE_DATASET_CATALOG


@router.get("/{dataset_id}")
async def get_dataset_details(
    dataset_id: str,
    search: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    ctx: TenantContext = Depends(require_permission(Permission.DATASOURCE_VIEW))
) -> Dict[str, Any]:
    """Fetch structured data rows, columns, and analytical statistics for a dataset."""
    matched = dataset_catalog.get_dataset(dataset_id)
    if not matched:
        # Also check by legacy alias or table name
        matched = dataset_catalog.get_dataset_by_table(dataset_id)
        if not matched:
            raise HTTPException(status_code=404, detail=f"Dataset with ID '{dataset_id}' not found.")

    return _query_curated_table_details(matched, limit=limit, offset=offset, search=search)


@router.get("/{dataset_id}/download")
async def download_dataset_csv(
    dataset_id: str,
    ctx: TenantContext = Depends(require_permission(Permission.QUERY_EXPORT))
):
    """Download curated dataset as CSV."""
    matched = dataset_catalog.get_dataset(dataset_id)
    if not matched:
        matched = dataset_catalog.get_dataset_by_table(dataset_id)
        if not matched:
            raise HTTPException(status_code=404, detail="Dataset not found.")

    primary_table = matched["tables"][0]
    raw_file = os.path.join(RAW_DATA_DIR, matched["dataset_id"], f"{primary_table}.csv")
    
    if os.path.exists(raw_file):
        return FileResponse(
            raw_file,
            media_type="text/csv",
            filename=f"{matched['dataset_id']}_{primary_table}.csv"
        )
    
    # Generate CSV from DuckDB on-the-fly
    conn = duckdb.connect(get_db_path())
    try:
        df = conn.execute(f"SELECT * FROM {primary_table} LIMIT 10000").df()
        csv_data = df.to_csv(index=False)
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={matched['dataset_id']}.csv"}
        )
    finally:
        conn.close()
