from typing import Optional, List
from pydantic import BaseModel, Field
from app.ai.tools.base import BaseTool
from app.core.permissions import Permission
from app.core.tenant import TenantContext


class GetSchemaCatalogInput(BaseModel):
    workspace_id: Optional[str] = None


class GetSchemaCatalogTool(BaseTool):
    name = "get_schema_catalog"
    description = "Retrieves schema catalog tables and sensitivity classifications for the current workspace."
    input_schema = GetSchemaCatalogInput
    required_permission = Permission.DATASOURCE_VIEW

    def _execute(self, inputs: GetSchemaCatalogInput, ctx: Optional[TenantContext]):
        from app.semantic.registry import schema_registry
        return schema_registry.get_tables(ctx.tenant_id if ctx else "tenant-acme")


class GetTableMetadataInput(BaseModel):
    table_name: str = Field(..., description="Name of table to inspect")


class GetTableMetadataTool(BaseTool):
    name = "get_table_metadata"
    description = "Retrieves column definitions, data types, primary keys, and security sensitivity for a table."
    input_schema = GetTableMetadataInput
    required_permission = Permission.DATASOURCE_VIEW

    def _execute(self, inputs: GetTableMetadataInput, ctx: Optional[TenantContext]):
        from app.semantic.registry import schema_registry
        return schema_registry.get_table_details(inputs.table_name)
