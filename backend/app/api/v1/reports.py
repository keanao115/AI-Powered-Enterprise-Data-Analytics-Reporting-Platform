import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.core.security import get_current_user_context, require_permission
from app.core.permissions import Permission
from app.core.tenant import TenantContext
from app.reporting.report_service import report_service

router = APIRouter(prefix="/reports", tags=["Reports"])


class CreateReportRequest(BaseModel):
    query_id: str
    title: str
    format: str = "pdf"


@router.post("")
async def create_report(
    req: CreateReportRequest,
    ctx: TenantContext = Depends(require_permission(Permission.REPORT_CREATE)),
):
    return report_service.create_report(req.query_id, req.title, req.format, ctx)


@router.get("/{report_id}/download")
async def download_report(
    report_id: str,
    ctx: TenantContext = Depends(require_permission(Permission.REPORT_DOWNLOAD)),
):
    output_dir = os.path.join("storage", "reports", ctx.tenant_id)
    for ext in (".pdf", ".xlsx", ".csv"):
        file_path = os.path.join(output_dir, f"{report_id}{ext}")
        if os.path.exists(file_path):
            return FileResponse(path=file_path, filename=f"report_{report_id}{ext}")
    
    # Fallback generated report for demo query downloads
    res = report_service.create_report(report_id, "Executive Sales & Returns Report", "pdf", ctx)
    return FileResponse(path=res["file_path"], filename=f"report_{report_id}.pdf")
