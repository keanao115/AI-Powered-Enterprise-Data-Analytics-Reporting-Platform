from fastapi import APIRouter, Depends

from app.core.permissions import Permission
from app.core.security import require_permission
from app.core.tenant import TenantContext
from app.semantic.registry import schema_registry

router = APIRouter(prefix="/schemas", tags=["Schemas"])


@router.get("")
async def get_schemas(ctx: TenantContext = Depends(require_permission(Permission.DATASOURCE_VIEW))):
    return schema_registry.get_tables(ctx.tenant_id)


@router.get("/catalog")
async def get_schema_catalog(ctx: TenantContext = Depends(require_permission(Permission.DATASOURCE_VIEW))):
    return [
        {
            "name": name,
            "desc": meta.get("description", ""),
            "columns": [
                {
                    "name": col_name,
                    "type": str(col_info.get("type", "VARCHAR")),
                    "classification": str(col_info.get("classification", "PUBLIC")),
                    "description": col_info.get("description", ""),
                }
                for col_name, col_info in meta.get("columns", {}).items()
            ],
        }
        for name, meta in schema_registry._catalog.items()
    ]


@router.get("/tables/{table_name}")
async def get_table_details(
    table_name: str,
    ctx: TenantContext = Depends(require_permission(Permission.DATASOURCE_VIEW)),
):
    return schema_registry.get_table_details(table_name)

