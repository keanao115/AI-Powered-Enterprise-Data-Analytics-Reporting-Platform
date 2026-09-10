import os
import csv
import io
from typing import List, Dict, Any, Optional
import duckdb
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import FileResponse, Response

from app.core.config import settings
from app.core.security import require_permission
from app.core.permissions import Permission
from app.core.tenant import TenantContext
from app.security.audit import audit_logger
from app.semantic.dataset_catalog import ENTERPRISE_DATASET_CATALOG, dataset_catalog
from app.query_engine.secure_gateway import secure_query_gateway
from app.security.data_masking import data_masking_engine

router = APIRouter(prefix="/datasets", tags=["Datasets"])

RAW_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/raw"))


def _query_curated_table_details(
    dataset: Dict[str, Any],
    ctx: TenantContext,
    limit: int = 50,
    offset: int = 0,
    search: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Queries dataset table through the Secure Query Gateway.
    Guarantees Invariant 1: Dataset Explorer enforces AST policy, logical RLS,
    column masking, and audit trails.
    """
    primary_table = dataset["tables"][0]
    capped_limit = min(limit, 200)

    # 1. Construct base query
    if search and search.strip():
        # Sanitize search term
        safe_q = search.strip().replace("'", "''")
        # Build wildcard search across columns
        query_sql = f"SELECT * FROM {primary_table} WHERE CAST({primary_table} AS VARCHAR) ILIKE '%{safe_q}%' LIMIT {capped_limit}"
    else:
        query_sql = f"SELECT * FROM {primary_table} LIMIT {capped_limit}"

    # 2. Execute via Secure Query Gateway with tenant context
    gateway_res = secure_query_gateway.execute(
        sql_query=query_sql,
        ctx=ctx,
        purpose="dataset_explorer",
        max_rows=capped_limit,
    )

    if not gateway_res.get("success"):
        # If table is not found or blocked by policy
        return {
            "metadata": dataset,
            "columns": [],
            "rows": [],
            "total_rows": 0,
            "column_stats": [],
            "error": gateway_res.get("error"),
        }

    query_data = gateway_res.get("result", {})
    columns = query_data.get("columns", [])
    raw_rows = query_data.get("rows", [])

    # Apply data masking for restricted PII attributes
    masked_rows = data_masking_engine.mask_result_set(columns, raw_rows)
    dict_rows = [dict(zip(columns, row)) for row in masked_rows]

    # Compute column profiling statistics
    stats = []
    for col in columns:
        sample_vals = [str(r[col]) for r in dict_rows[:3] if col in r and r[col] is not None]
        stats.append({
            "column_name": col,
            "type": "VARCHAR",
            "sample_values": sample_vals,
        })

    return {
        "metadata": dataset,
        "columns": columns,
        "rows": dict_rows,
        "total_rows": len(dict_rows),
        "column_stats": stats,
        "tables": dataset.get("tables", [primary_table]),
    }


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
        matched = dataset_catalog.get_dataset_by_table(dataset_id)
        if not matched:
            raise HTTPException(status_code=404, detail=f"Dataset with ID '{dataset_id}' not found.")

    return _query_curated_table_details(matched, ctx=ctx, limit=limit, offset=offset, search=search)


@router.get("/{dataset_id}/download")
async def download_dataset_csv(
    dataset_id: str,
    ctx: TenantContext = Depends(require_permission(Permission.QUERY_EXPORT))
):
    """
    Download curated dataset as CSV through Secure Query Gateway with RLS, CLS, and max row limits.
    """
    matched = dataset_catalog.get_dataset(dataset_id)
    if not matched:
        matched = dataset_catalog.get_dataset_by_table(dataset_id)
        if not matched:
            raise HTTPException(status_code=404, detail="Dataset not found.")

    primary_table = matched["tables"][0]
    export_limit = getattr(settings, "MAX_EXPORT_ROWS", 50000)

    # Route export query through the Secure Query Gateway
    export_sql = f"SELECT * FROM {primary_table} LIMIT {export_limit}"
    gateway_res = secure_query_gateway.execute(
        sql_query=export_sql,
        ctx=ctx,
        purpose="dataset_csv_export",
        max_rows=export_limit,
    )

    if not gateway_res.get("success"):
        raise HTTPException(
            status_code=400,
            detail=f"Export failed: {gateway_res.get('error', 'Query policy blocked')}",
        )

    query_data = gateway_res.get("result", {})
    columns = query_data.get("columns", [])
    rows = query_data.get("rows", [])

    # Mask sensitive columns if user lacks unmasked export privileges
    user_perms = set(ctx.permissions)
    if Permission.DATA_RESTRICTED_READ.value not in user_perms and Permission.DATA_RESTRICTED_READ not in user_perms:
        rows = data_masking_engine.mask_result_set(columns, rows)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(columns)
    writer.writerows(rows)

    audit_logger.log_event(
        action="DATASET_EXPORTED",
        resource=dataset_id,
        result="SUCCESS",
        risk_level="MEDIUM",
        reason=f"Exported {len(rows)} rows from {primary_table}",
        ctx=ctx,
    )

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={matched['dataset_id']}_{primary_table}.csv"}
    )
