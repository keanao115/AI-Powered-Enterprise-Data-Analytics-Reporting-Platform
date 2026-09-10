from fastapi import APIRouter, Depends, Query

from app.core.permissions import Permission, Role
from app.core.security import require_permission
from app.core.tenant import TenantContext
from app.security.audit import audit_logger

router = APIRouter(prefix="/audit", tags=["Audit Logs"])


@router.get("")
async def get_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    ctx: TenantContext = Depends(require_permission(Permission.AUDIT_VIEW)),
):
    """
    Returns immutable audit logs filtered by tenant boundary.
    Super Admins and Compliance Officers can view across all tenants.
    """
    is_super = (
        Role.SUPER_ADMIN in getattr(ctx, "roles", [])
        or ctx.user_role == Role.SUPER_ADMIN
        or "compliance_officer" in [str(r).lower() for r in getattr(ctx, "roles", [])]
    )
    target_tenant = None if is_super else ctx.tenant_id
    return audit_logger.get_events(tenant_id=target_tenant, limit=limit)
