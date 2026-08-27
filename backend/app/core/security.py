from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.core.exceptions import AuthenticationException, AuthorizationDeniedException
from app.core.permissions import Role, Permission, has_permission, ROLE_PERMISSIONS
from app.core.tenant import TenantContext, set_tenant_context


class DataClassification(str, Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    RESTRICTED = "RESTRICTED"


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        raise AuthenticationException("Could not validate credentials")


async def get_current_user_context(
    token: Optional[str] = Depends(oauth2_scheme),
) -> TenantContext:
    if not token:
        # Fallback default tenant for local demo / unauthenticated demo testing if enabled
        ctx = TenantContext(
            tenant_id="tenant-acme",
            organization_id="org-acme-corp",
            workspace_id="ws-sales-analytics",
            user_id="usr-demo-001",
            roles=[Role.ORG_ADMIN],
            permissions=[
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
                Permission.DATA_RESTRICTED_READ,
                Permission.SANDBOX_EXECUTE,
                Permission.EVALUATION_RUN,
            ],
            session_id="sess-demo-local",
        )
        set_tenant_context(ctx)
        return ctx

    payload = decode_access_token(token)
    role_str = payload.get("role", Role.VIEWER)
    try:
        role = Role(role_str)
    except ValueError:
        role = Role.VIEWER

    ctx = TenantContext(
        tenant_id=payload.get("tenant_id", "default"),
        organization_id=payload.get("organization_id", "default"),
        workspace_id=payload.get("workspace_id", "default"),
        user_id=payload.get("sub", "anonymous"),
        roles=[role],
        permissions=list(ROLE_PERMISSIONS.get(role, set())),
        session_id=payload.get("session_id", "sess-unknown"),
    )
    set_tenant_context(ctx)
    return ctx


def require_permission(permission: Permission):
    async def permission_dependency(
        ctx: TenantContext = Depends(get_current_user_context),
    ) -> TenantContext:
        user_perms = set(ctx.permissions)
        # Check direct or role-derived
        if permission.value not in user_perms and permission not in user_perms:
            raise AuthorizationDeniedException(
                f"Missing required permission: {permission.value}"
            )
        return ctx

    return permission_dependency
