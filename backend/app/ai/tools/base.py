from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type
from pydantic import BaseModel
from app.core.tenant import TenantContext, get_tenant_context
from app.core.permissions import Permission, has_permission, Role


class BaseTool(ABC):
    name: str
    description: str
    input_schema: Type[BaseModel]
    required_permission: Optional[Permission] = None
    risk_level: str = "LOW"  # LOW, MEDIUM, HIGH, CRITICAL

    def validate_authorization(self, ctx: TenantContext) -> bool:
        if not self.required_permission:
            return True
        user_role = Role(ctx.user_role)
        return has_permission(user_role, self.required_permission)

    def run(self, **kwargs: Any) -> Dict[str, Any]:
        ctx = get_tenant_context()
        if ctx and not self.validate_authorization(ctx):
            return {
                "success": False,
                "error": f"Authorization denied: Tool '{self.name}' requires permission '{self.required_permission}'",
            }
        try:
            validated_inputs = self.input_schema(**kwargs)
            result = self._execute(validated_inputs, ctx)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @abstractmethod
    def _execute(self, inputs: BaseModel, ctx: Optional[TenantContext]) -> Any:
        pass
