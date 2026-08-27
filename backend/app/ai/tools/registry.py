from typing import Any, Dict, List, Optional
from app.ai.tools.base import BaseTool
from app.ai.tools.schema_tools import GetSchemaCatalogTool, GetTableMetadataTool
from app.ai.tools.semantic_tools import GetSemanticMetricTool
from app.ai.tools.sql_tools import ExecuteReadOnlyQueryTool
from app.ai.tools.analytics_tools import RunDataQualityCheckTool, RunSandboxAnalysisTool
from app.ai.tools.visualization_tools import GenerateVisualizationTool
from app.ai.tools.reporting_tools import GenerateReportTool
from app.ai.tools.provenance_tools import GetProvenanceTool


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._register_default_tools()

    def register_tool(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    def _register_default_tools(self) -> None:
        defaults = [
            GetSchemaCatalogTool(),
            GetTableMetadataTool(),
            GetSemanticMetricTool(),
            ExecuteReadOnlyQueryTool(),
            RunDataQualityCheckTool(),
            RunSandboxAnalysisTool(),
            GenerateVisualizationTool(),
            GenerateReportTool(),
            GetProvenanceTool(),
        ]
        for tool in defaults:
            self.register_tool(tool)

    def get_tool(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name)

    def list_tools(self) -> List[Dict[str, Any]]:
        tool_definitions = []
        for tool in self._tools.values():
            tool_definitions.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.input_schema.model_json_schema(),
                }
            })
        return tool_definitions

    def execute_tool(self, name: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        tool = self.get_tool(name)
        if not tool:
            return {"success": False, "error": f"Tool '{name}' is not registered in ToolRegistry"}
        return tool.run(**kwargs)


tool_registry = ToolRegistry()
