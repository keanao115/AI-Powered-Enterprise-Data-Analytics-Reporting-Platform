import os
import re

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.core.permissions import Permission, Role
from app.core.security import require_permission
from app.core.tenant import TenantContext
from app.reporting.report_service import report_service

router = APIRouter(prefix="/reports", tags=["Reports"])

SAFE_REPORT_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{3,64}$")


class CreateReportRequest(BaseModel):
    query_id: str = Field(..., description="Query ID associated with this report")
    title: str = Field(..., description="Report title")
    format: str = Field("pdf", description="Output format: pdf, excel, csv")


@router.post("")
async def create_report(
    req: CreateReportRequest,
    ctx: TenantContext = Depends(require_permission(Permission.REPORT_CREATE)),
):
    valid_formats = {"pdf", "excel", "xlsx", "csv"}
    if req.format.lower() not in valid_formats:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format '{req.format}'. Supported: pdf, excel, csv.",
        )
    return report_service.create_report(req.query_id, req.title, req.format, ctx)


@router.get("/{report_id}/download")
async def download_report(
    report_id: str,
    ctx: TenantContext = Depends(require_permission(Permission.REPORT_DOWNLOAD)),
):
    """
    Downloads generated report with resource ownership validation and path traversal defense.
    Guarantees Invariant 2: No report can be downloaded without resource ownership verification.
    """
    # 1. Path Traversal & Identifier Pattern Validation
    if (
        not SAFE_REPORT_ID_PATTERN.match(report_id)
        or ".." in report_id
        or "/" in report_id
        or "\\" in report_id
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid report_id format: Path traversal characters are prohibited.",
        )

    base_dir = os.path.abspath(os.path.join("storage", "reports", ctx.tenant_id))

    # 2. Check Registry Resource Ownership
    registered = report_service.get_report(report_id)
    if registered:
        is_super_admin = Role.SUPER_ADMIN in ctx.roles or ctx.user_role == Role.SUPER_ADMIN
        if registered.get("tenant_id") != ctx.tenant_id and not is_super_admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report '{report_id}' not found.",
            )
        resolved_path = os.path.abspath(registered["file_path"])
        if not resolved_path.startswith(base_dir):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Security Violation: Path traversal outside tenant storage boundary.",
            )
        if os.path.exists(resolved_path):
            ext = os.path.splitext(resolved_path)[1]
            return FileResponse(path=resolved_path, filename=f"report_{report_id}{ext}")

    # 3. Check physical file inside tenant-isolated folder
    for ext in (".pdf", ".xlsx", ".csv"):
        target_file = os.path.abspath(os.path.join(base_dir, f"{report_id}{ext}"))
        if not target_file.startswith(base_dir):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Security Violation: Path traversal outside tenant storage boundary.",
            )
        if os.path.exists(target_file):
            return FileResponse(path=target_file, filename=f"report_{report_id}{ext}")

    # 4. Safe demo fallback only for explicit demo query IDs
    if report_id.startswith("req-demo") or report_id == "rep-demo-001":
        res = report_service.create_report(
            report_id, "Executive Sales & Returns Report", "pdf", ctx
        )
        return FileResponse(path=res["file_path"], filename=f"report_{report_id}.pdf")

    # If not found, return 404 (do not generate on arbitrary unknown IDs)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Report '{report_id}' not found in tenant repository.",
    )
