from typing import Any, Dict, List
from pydantic import BaseModel, Field
from app.ai.tools.base import BaseTool
from app.core.permissions import Permission
from app.core.tenant import TenantContext


class RunDataQualityCheckInput(BaseModel):
    columns: List[str]
    rows: List[List[Any]]


class RunDataQualityCheckTool(BaseTool):
    name = "run_data_quality_check"
    description = "Evaluates dataset completeness, null rates, freshness, and duplicates to produce a Data Quality Score."
    input_schema = RunDataQualityCheckInput
    required_permission = Permission.QUERY_EXECUTE

    def _execute(self, inputs: RunDataQualityCheckInput, ctx: Optional[TenantContext]):
        from app.analytics.data_quality import evaluate_data_quality
        return evaluate_data_quality(inputs.columns, inputs.rows)


class RunSandboxAnalysisInput(BaseModel):
    python_code: str = Field(..., description="Pandas/Numpy analytical code to run")
    data: Dict[str, Any] = Field(..., description="Input dataframe dictionary")


class RunSandboxAnalysisTool(BaseTool):
    name = "run_sandbox_analysis"
    description = "Executes analytical Python code inside an isolated, process/AST-restricted sandbox environment."
    input_schema = RunSandboxAnalysisInput
    required_permission = Permission.SANDBOX_EXECUTE
    risk_level = "HIGH"

    def _execute(self, inputs: RunSandboxAnalysisInput, ctx: Optional[TenantContext]):
        from app.sandbox.runner import sandbox_runner
        return sandbox_runner.run_code(inputs.python_code, inputs.data)
