import asyncio
import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.core.security import get_current_user_context
from app.core.tenant import TenantContext

router = APIRouter(prefix="/jobs", tags=["Asynchronous Jobs"])


@router.get("/{job_id}")
async def get_job_status(job_id: str, ctx: TenantContext = Depends(get_current_user_context)):
    return {
        "job_id": job_id,
        "tenant_id": ctx.tenant_id,
        "status": "SUCCEEDED",
        "progress_percentage": 100,
        "current_step": "COMPLETED",
    }


@router.get("/{job_id}/stream")
async def stream_job_progress(job_id: str):
    async def event_generator():
        steps = [
            ("REQUEST_RECEIVED", 10),
            ("SECURITY_SCREENING", 25),
            ("SCHEMA_SEMANTIC_RETRIEVAL", 40),
            ("SQL_GENERATION", 55),
            ("SQL_AST_POLICY_AND_RLS", 70),
            ("DATABASE_EXECUTION", 85),
            ("INSIGHT_GROUNDING", 95),
            ("COMPLETED", 100),
        ]
        for step_name, pct in steps:
            data = json.dumps({"job_id": job_id, "step": step_name, "progress": pct})
            yield f"data: {data}\n\n"
            await asyncio.sleep(0.1)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
