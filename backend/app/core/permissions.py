from enum import Enum
from typing import Set


class Role(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ORG_ADMIN = "ORG_ADMIN"
    ANALYST = "ANALYST"
    VIEWER = "VIEWER"
    DATA_STEWARD = "DATA_STEWARD"


class Permission(str, Enum):
    QUERY_EXECUTE = "query:execute"
    QUERY_SQL = "query:sql"
    QUERY_EXPORT = "query:export"
    QUERY_HISTORY = "query:history"
    REPORT_CREATE = "report:create"
    REPORT_DOWNLOAD = "report:download"
    DATASOURCE_VIEW = "datasource:view"
    DATASOURCE_MANAGE = "datasource:manage"
    SEMANTIC_VIEW = "semantic:view"
    SEMANTIC_MANAGE = "semantic:manage"
    AUDIT_VIEW = "audit:view"
    USERS_MANAGE = "users:manage"
    ORGANIZATION_MANAGE = "organization:manage"
    DATA_RESTRICTED_READ = "data:restricted:read"
    SANDBOX_EXECUTE = "sandbox:execute"
    EVALUATION_RUN = "evaluation:run"


ROLE_PERMISSIONS: dict[Role, Set[Permission]] = {
    Role.SUPER_ADMIN: set(Permission),
    Role.ORG_ADMIN: {
        Permission.QUERY_EXECUTE,
        Permission.QUERY_SQL,
        Permission.QUERY_EXPORT,
        Permission.QUERY_HISTORY,
        Permission.REPORT_CREATE,
        Permission.REPORT_DOWNLOAD,
        Permission.DATASOURCE_VIEW,
        Permission.DATASOURCE_MANAGE,
        Permission.SEMANTIC_VIEW,
        Permission.SEMANTIC_MANAGE,
        Permission.AUDIT_VIEW,
        Permission.USERS_MANAGE,
        Permission.ORGANIZATION_MANAGE,
        Permission.DATA_RESTRICTED_READ,
        Permission.SANDBOX_EXECUTE,
        Permission.EVALUATION_RUN,
    },
    Role.DATA_STEWARD: {
        Permission.QUERY_EXECUTE,
        Permission.QUERY_SQL,
        Permission.QUERY_HISTORY,
        Permission.DATASOURCE_VIEW,
        Permission.DATASOURCE_MANAGE,
        Permission.SEMANTIC_VIEW,
        Permission.SEMANTIC_MANAGE,
        Permission.AUDIT_VIEW,
        Permission.DATA_RESTRICTED_READ,
        Permission.EVALUATION_RUN,
    },
    Role.ANALYST: {
        Permission.QUERY_EXECUTE,
        Permission.QUERY_SQL,
        Permission.QUERY_EXPORT,
        Permission.QUERY_HISTORY,
        Permission.REPORT_CREATE,
        Permission.REPORT_DOWNLOAD,
        Permission.DATASOURCE_VIEW,
        Permission.SEMANTIC_VIEW,
        Permission.SANDBOX_EXECUTE,
        Permission.EVALUATION_RUN,
    },
    Role.VIEWER: {
        Permission.QUERY_EXECUTE,
        Permission.QUERY_HISTORY,
        Permission.REPORT_DOWNLOAD,
        Permission.DATASOURCE_VIEW,
        Permission.SEMANTIC_VIEW,
    },
}


def has_permission(role: Role, permission: Permission) -> bool:
    perms = ROLE_PERMISSIONS.get(role, set())
    return permission in perms
