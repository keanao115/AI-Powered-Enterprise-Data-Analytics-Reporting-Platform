from fastapi import APIRouter, Depends
from app.core.security import get_current_user_context, require_permission
from app.core.permissions import Permission
from app.core.tenant import TenantContext
from app.semantic.registry import schema_registry
from app.semantic.semantic_layer import semantic_layer

schemas_router = APIRouter(prefix="/schemas", tags=["Schemas"])
metrics_router = APIRouter(prefix="/metrics", tags=["Metrics"])


@schemas_router.get("")
async def get_schemas(ctx: TenantContext = Depends(require_permission(Permission.DATASOURCE_VIEW))):
    return schema_registry.get_tables(ctx.tenant_id)


@schemas_router.get("/tables/{table_name}")
async def get_table_details(
    table_name: str,
    ctx: TenantContext = Depends(require_permission(Permission.DATASOURCE_VIEW)),
):
    return schema_registry.get_table_details(table_name)


@metrics_router.get("")
async def get_metrics(ctx: TenantContext = Depends(require_permission(Permission.SEMANTIC_VIEW))):
    return semantic_layer.list_metrics(ctx.tenant_id)


@metrics_router.get("/{metric_name}")
async def get_metric_details(
    metric_name: str,
    ctx: TenantContext = Depends(require_permission(Permission.SEMANTIC_VIEW)),
):
    return semantic_layer.get_metric(metric_name)
