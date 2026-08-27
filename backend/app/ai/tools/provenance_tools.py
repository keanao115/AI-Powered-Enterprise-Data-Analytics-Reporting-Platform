from typing import Optional
from pydantic import BaseModel, Field
from app.ai.tools.base import BaseTool
from app.core.permissions import Permission
from app.core.tenant import TenantContext


class GetProvenanceInput(BaseModel):
    query_id: str = Field(..., description="Query ID to retrieve lineage for")


class GetProvenanceTool(BaseTool):
    name = "get_provenance"
    description = "Retrieves full data provenance tree (User Question -> Intent -> Semantic Metric -> AST SQL -> Executed DB Plan -> Data Quality -> Insight)."
    input_schema = GetProvenanceInput
    required_permission = Permission.QUERY_HISTORY

    def _execute(self, inputs: GetProvenanceInput, ctx: Optional[TenantContext]):
        from app.analytics.provenance import provenance_service
        return provenance_service.get_lineage(inputs.query_id, ctx)
