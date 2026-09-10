from fastapi import APIRouter, Depends

from app.core.permissions import Permission
from app.core.security import require_permission
from app.core.tenant import TenantContext
from app.semantic.semantic_layer import semantic_layer

metrics_router = APIRouter(prefix="/metrics", tags=["Metrics"])


@metrics_router.get("")
async def get_metrics(ctx: TenantContext = Depends(require_permission(Permission.SEMANTIC_VIEW))):
    return semantic_layer.list_metrics(ctx.tenant_id)


@metrics_router.get("/{metric_name}")
async def get_metric_details(
    metric_name: str,
    ctx: TenantContext = Depends(require_permission(Permission.SEMANTIC_VIEW)),
):
    return semantic_layer.get_metric(metric_name)
