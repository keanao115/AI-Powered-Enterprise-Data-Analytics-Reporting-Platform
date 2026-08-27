import contextvars
from typing import Optional, List
from dataclasses import dataclass, field


@dataclass
class TenantContext:
    tenant_id: str = "tenant-acme"
    organization_id: str = "org-acme-corp"
    workspace_id: str = "ws-sales-analytics"
    user_id: str = "usr-demo-001"
    user_role: str = "Admin"
    authorized_regions: List[str] = field(default_factory=lambda: ["US", "EU", "APAC"])
    authorized_departments: List[str] = field(default_factory=lambda: ["Sales", "Finance", "Operations"])
    roles: List[str] = field(default_factory=lambda: ["Admin"])
    permissions: List[str] = field(default_factory=lambda: [
        "query:execute", "query:sql", "query:export", "query:history",
        "report:create", "report:download", "datasource:view", "datasource:manage",
        "semantic:view", "semantic:manage", "audit:view", "evaluation:run",
        "data:restricted:read", "sandbox:execute"
    ])
    session_id: str = "sess-demo-local"


_tenant_context_var: contextvars.ContextVar[Optional[TenantContext]] = contextvars.ContextVar(
    "tenant_context", default=None
)


def set_tenant_context(ctx: TenantContext) -> None:
    _tenant_context_var.set(ctx)


def get_tenant_context() -> Optional[TenantContext]:
    return _tenant_context_var.get()


def clear_tenant_context() -> None:
    _tenant_context_var.set(None)


def require_tenant_context() -> TenantContext:
    ctx = get_tenant_context()
    if ctx is None:
        return TenantContext()
    return ctx
