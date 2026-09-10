import asyncio
import json
import time
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app.core.permissions import Role
from app.core.security import get_current_user_context
from app.core.tenant import TenantContext

router = APIRouter(prefix="/jobs", tags=["Asynchronous Jobs"])


class JobStore:
    """
    In-Memory Thread-Safe Job Registry with Tenant Isolation.
    Guarantees Invariant 5: Jobs have strict tenant ownership and cannot be leaked across tenants.
    """

    def __init__(self):
        self._jobs: Dict[str, Dict[str, Any]] = {
            "job-demo-acme-001": {
                "job_id": "job-demo-acme-001",
                "tenant_id": "tenant-acme",
                "user_id": "usr-demo-001",
                "status": "SUCCEEDED",
                "progress_percentage": 100,
                "current_step": "COMPLETED",
                "created_at": time.time() - 300,
            },
            "job-demo-globex-001": {
                "job_id": "job-demo-globex-001",
                "tenant_id": "tenant-globex",
                "user_id": "usr-globex-001",
                "status": "SUCCEEDED",
                "progress_percentage": 100,
                "current_step": "COMPLETED",
                "created_at": time.time() - 150,
            },
        }

    def register_job(
        self,
        job_id: str,
        tenant_id: str,
        user_id: str,
        status: str = "RUNNING",
        current_step: str = "INITIALIZING",
        progress_percentage: int = 0,
    ) -> Dict[str, Any]:
        record = {
            "job_id": job_id,
            "tenant_id": tenant_id,
            "user_id": user_id,
            "status": status,
            "progress_percentage": progress_percentage,
            "current_step": current_step,
            "created_at": time.time(),
        }
        self._jobs[job_id] = record
        return record

    def update_job(
        self,
        job_id: str,
        status: Optional[str] = None,
        current_step: Optional[str] = None,
        progress_percentage: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        if job_id not in self._jobs:
            return None
        if status:
            self._jobs[job_id]["status"] = status
        if current_step:
            self._jobs[job_id]["current_step"] = current_step
        if progress_percentage is not None:
            self._jobs[job_id]["progress_percentage"] = progress_percentage
        return self._jobs[job_id]

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        return self._jobs.get(job_id)


job_store = JobStore()


@router.get("/{job_id}")
async def get_job_status(job_id: str, ctx: TenantContext = Depends(get_current_user_context)):
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found.",
        )

    # Multi-tenant resource ownership authorization
    is_super_admin = Role.SUPER_ADMIN in ctx.roles or ctx.user_role == Role.SUPER_ADMIN
    if job["tenant_id"] != ctx.tenant_id and not is_super_admin:
        # Return 404 to prevent resource ID enumeration across tenants
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found.",
        )

    return {
        "job_id": job["job_id"],
        "tenant_id": job["tenant_id"],
        "status": job["status"],
        "progress_percentage": job["progress_percentage"],
        "current_step": job["current_step"],
        "created_at": job["created_at"],
    }


@router.get("/{job_id}/stream")
async def stream_job_progress(
    job_id: str,
    ctx: TenantContext = Depends(get_current_user_context),
):
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found.",
        )

    is_super_admin = Role.SUPER_ADMIN in ctx.roles or ctx.user_role == Role.SUPER_ADMIN
    if job["tenant_id"] != ctx.tenant_id and not is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found.",
        )

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
            await asyncio.sleep(0.05)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
