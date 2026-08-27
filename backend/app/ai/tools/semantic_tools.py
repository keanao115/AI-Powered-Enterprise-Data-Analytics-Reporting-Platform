from typing import Optional
from pydantic import BaseModel, Field
from app.ai.tools.base import BaseTool
from app.core.permissions import Permission
from app.core.tenant import TenantContext


class GetSemanticMetricInput(BaseModel):
    metric_name: str = Field(..., description="Business metric name, e.g. Revenue, Return Rate, MoM Growth")


class GetSemanticMetricTool(BaseTool):
    name = "get_semantic_metric"
    description = "Retrieves semantic formula, allowed dimensions, and base table mapping for a business metric."
    input_schema = GetSemanticMetricInput
    required_permission = Permission.SEMANTIC_VIEW

    def _execute(self, inputs: GetSemanticMetricInput, ctx: Optional[TenantContext]):
        from app.semantic.semantic_layer import semantic_layer
        return semantic_layer.get_metric(inputs.metric_name)
