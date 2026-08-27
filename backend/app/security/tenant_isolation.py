from typing import Any, Dict, Optional
from app.core.tenant import TenantContext
from app.core.exceptions import TenantAccessDeniedException


class TenantIsolationValidator:
    """
    Validates that resource access matches authoritative TenantContext.
    """

    def validate_tenant_access(self, resource_tenant_id: str, ctx: TenantContext) -> bool:
        if not ctx or not ctx.tenant_id:
            raise TenantAccessDeniedException("Missing tenant context")
        if resource_tenant_id != ctx.tenant_id:
            raise TenantAccessDeniedException(
                f"Cross-tenant violation: User tenant '{ctx.tenant_id}' cannot access resource tenant '{resource_tenant_id}'"
            )
        return True


tenant_isolation = TenantIsolationValidator()
