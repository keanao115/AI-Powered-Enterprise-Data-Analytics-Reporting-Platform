import threading
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from app.ai.agent.analyst_agent import analyst_agent
from app.core.permissions import Permission
from app.core.security import require_permission
from app.core.tenant import TenantContext
from app.security.data_masking import data_masking_engine

router = APIRouter(prefix="/queries", tags=["Queries"])

_query_lock = threading.Lock()
_query_cache: Dict[str, Dict[str, Any]] = {}
_query_history_store: List[Dict[str, Any]] = [
    {
        "query_id": "req-demo-001",
        "tenant_id": "tenant-acme",
        "user_id": "usr-demo-001",
        "question": "Compare Sales team revenue growth between last month and this month",
        "status": "SUCCEEDED",
        "execution_time_ms": 42.5,
        "row_count": 3,
        "created_at": "2026-08-11T20:00:00Z",
    },
    {
        "query_id": "req-demo-002",
        "tenant_id": "tenant-acme",
        "user_id": "usr-demo-001",
        "question": "Find the top 10 products by revenue",
        "status": "SUCCEEDED",
        "execution_time_ms": 18.2,
        "row_count": 10,
        "created_at": "2026-08-11T19:30:00Z",
    },
    {
        "query_id": "req-demo-003",
        "tenant_id": "tenant-acme",
        "user_id": "usr-demo-001",
        "question": "Show customer SSNs",
        "status": "BLOCKED",
        "execution_time_ms": 2.1,
        "row_count": 0,
        "created_at": "2026-08-11T19:00:00Z",
    },
]


def get_cached_query(query_id: str) -> Optional[Dict[str, Any]]:
    with _query_lock:
        return _query_cache.get(query_id)


class QueryRequest(BaseModel):
    question: str
    workspace_id: Optional[str] = None
    dataset_id: Optional[str] = None


@router.post("")
def execute_query(
    req: QueryRequest,
    ctx: TenantContext = Depends(require_permission(Permission.QUERY_EXECUTE)),
):
    try:
        state = analyst_agent.execute_pipeline(req.question, ctx, dataset_id=req.dataset_id)

        # Apply column masking for restricted attributes before UI presentation
        res_data = state.analytical_results
        if "columns" in res_data and "rows" in res_data:
            masked_rows = data_masking_engine.mask_result_set(res_data["columns"], res_data["rows"])
            res_data["rows"] = masked_rows

        # Record dynamically into history & cache
        exec_time = getattr(state, "query_result_metadata", {}).get("execution_time_ms", 12.5)
        row_cnt = getattr(state, "query_result_metadata", {}).get("row_count", len(res_data.get("rows", [])))
        record = {
            "query_id": state.request_id,
            "tenant_id": ctx.tenant_id,
            "user_id": ctx.user_id,
            "question": state.original_question,
            "status": "SUCCEEDED",
            "execution_time_ms": exec_time,
            "row_count": row_cnt,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        with _query_lock:
            _query_history_store.insert(0, record)
            _query_cache[state.request_id] = {
                "question": state.original_question,
                "tenant_id": ctx.tenant_id,
                "data": res_data,
                "claims": state.claims,
                "summary": res_data.get("summary", ""),
            }

        return {
            "query_id": state.request_id,
            "status": "SUCCEEDED",
            "question": state.original_question,
            "generated_sql": state.generated_sql,
            "rewritten_sql": state.validated_sql,
            "execution_steps": state.execution_steps,
            "data_quality": state.data_quality,
            "analytical_results": res_data,
            "visualization": state.visualization_metadata,
            "claims": state.claims,
            "grounding_status": state.grounding_status,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": str(e)},
        ) from e


@router.get("/history")
async def get_query_history(
    limit: int = Query(50, ge=1, le=200),
    ctx: TenantContext = Depends(require_permission(Permission.QUERY_HISTORY)),
):
    with _query_lock:
        items = [q for q in _query_history_store if q.get("tenant_id") == ctx.tenant_id]
    return items[:limit]
