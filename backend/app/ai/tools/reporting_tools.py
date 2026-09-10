from typing import Any, Dict, List
from pydantic import BaseModel, Field
from app.ai.tools.base import BaseTool
from app.core.permissions import Permission
from app.core.tenant import TenantContext


from app.ai.tools.visualization_tools import (
    GenerateVisualizationInput,
    GenerateVisualizationTool,
)


class GenerateReportInput(BaseModel):
    query_id: str
    title: str
    format: str = Field("pdf", description="pdf, excel, csv")


class GenerateReportTool(BaseTool):
    name = "generate_report"
    description = "Generates audit-ready PDF, Excel, or CSV report for an executed query result."
    input_schema = GenerateReportInput
    required_permission = Permission.REPORT_CREATE
    risk_level = "MEDIUM"

    def _execute(self, inputs: GenerateReportInput, ctx: Optional[TenantContext]):
        from app.reporting.report_service import report_service
        return report_service.create_report(inputs.query_id, inputs.title, inputs.format, ctx)
