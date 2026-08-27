from typing import Any, Dict, List
from pydantic import BaseModel, Field
from app.ai.tools.base import BaseTool
from app.core.permissions import Permission
from app.core.tenant import TenantContext


class GenerateVisualizationInput(BaseModel):
    chart_type: str = Field(..., description="bar, line, pie, scatter")
    title: str
    x_column: str
    y_column: str
    data: Dict[str, Any]


class GenerateVisualizationTool(BaseTool):
    name = "generate_visualization"
    description = "Generates chart configuration and base64 matplotlib/seaborn plot image from query results."
    input_schema = GenerateVisualizationInput
    required_permission = Permission.QUERY_EXECUTE

    def _execute(self, inputs: GenerateVisualizationInput, ctx: Optional[TenantContext]):
        from app.sandbox.runner import sandbox_runner
        chart_code = f"""
import matplotlib.pyplot as plt
import pandas as pd
import io, base64

df = pd.DataFrame(data['rows'], columns=data['columns'])
plt.figure(figsize=(8, 4.5))
plt.bar(df['{inputs.x_column}'], df['{inputs.y_column}'], color='#3b82f6')
plt.title('{inputs.title}')
plt.xlabel('{inputs.x_column}')
plt.ylabel('{inputs.y_column}')
plt.tight_layout()

buf = io.BytesIO()
plt.savefig(buf, format='png')
buf.seek(0)
img_b64 = base64.b64encode(buf.read()).decode('utf-8')
result = {{'chart_type': '{inputs.chart_type}', 'image_base64': img_b64}}
"""
        return sandbox_runner.run_code(chart_code, inputs.data)


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
