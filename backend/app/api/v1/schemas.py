from fastapi import APIRouter, Depends
from app.core.security import require_permission
from app.core.permissions import Permission
from app.core.tenant import TenantContext
from app.semantic.registry import schema_registry

router = APIRouter(prefix="/schemas", tags=["Schemas"])


@router.get("")
async def get_schemas(ctx: TenantContext = Depends(require_permission(Permission.DATASOURCE_VIEW))):
    return schema_registry.get_tables(ctx.tenant_id)


@router.get("/tables/{table_name}")
async def get_table_details(
    table_name: str,
    ctx: TenantContext = Depends(require_permission(Permission.DATASOURCE_VIEW)),
):
    return schema_registry.get_table_details(table_name)
