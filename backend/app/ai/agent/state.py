from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AgentState(BaseModel):
    request_id: str
    tenant_id: str
    organization_id: str
    workspace_id: str
    user_id: str
    user_permissions: List[str] = Field(default_factory=list)
    original_question: str
    normalized_question: str = ""
    intent: str = "ANALYTICAL_QUERY"
    clarification_status: str = "NOT_NEEDED"  # NOT_NEEDED, REQUIRED, RESOLVED
    clarification_options: List[str] = Field(default_factory=list)
    semantic_context: Dict[str, Any] = Field(default_factory=dict)
    selected_tools: List[str] = Field(default_factory=list)
    generated_sql: Optional[str] = None
    validated_sql: Optional[str] = None
    query_result_metadata: Dict[str, Any] = Field(default_factory=dict)
    data_quality: Dict[str, Any] = Field(default_factory=dict)
    analytical_results: Dict[str, Any] = Field(default_factory=dict)
    visualization_metadata: Dict[str, Any] = Field(default_factory=dict)
    claims: List[Dict[str, Any]] = Field(default_factory=list)
    grounding_status: str = "PASSED"
    report_id: Optional[str] = None
    errors: List[str] = Field(default_factory=list)
    execution_steps: List[Dict[str, Any]] = Field(default_factory=list)
