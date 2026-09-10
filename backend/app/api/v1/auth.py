from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password, get_current_user_context
from app.core.tenant import TenantContext

router = APIRouter(prefix="/auth", tags=["Authentication"])


from app.security.login_limiter import login_rate_limiter
from app.security.audit import audit_logger


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    tenant_id: str
    role: str
    idp_provider: Optional[str] = "local"


class SSOProviderInfo(BaseModel):
    id: str
    name: str
    protocol: str
    enabled: bool
    login_url: str


class OIDCCallbackRequest(BaseModel):
    provider: str = "keycloak"
    id_token: str
    tenant_id: Optional[str] = None


@router.post("/login", response_model=LoginResponse)
async def login(req: LoginRequest):
    email_clean = req.email.lower().strip()

    # 1. Check brute-force lockout status
    is_locked, remaining_lock = login_rate_limiter.is_locked(email_clean)
    if is_locked:
        audit_logger.log_event(
            action="LOGIN_BLOCKED",
            resource=email_clean,
            result="BLOCKED",
            risk_level="HIGH",
            reason=f"Account locked out. Brute-force threshold exceeded. Retry after {remaining_lock}s.",
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many failed login attempts. Account temporarily locked for {remaining_lock} seconds to protect against brute-force attacks.",
            headers={"Retry-After": str(remaining_lock)},
        )

    # 2. Multi-tenant demo users: Acme Corp & Globex Corp
    DEMO_USERS = {
        "admin@acme.com": {"tenant_id": "tenant-acme", "org_id": "org-acme-corp", "ws_id": "ws-sales-analytics", "role": "ORG_ADMIN"},
        "analyst@acme.com": {"tenant_id": "tenant-acme", "org_id": "org-acme-corp", "ws_id": "ws-sales-analytics", "role": "ANALYST"},
        "viewer@acme.com": {"tenant_id": "tenant-acme", "org_id": "org-acme-corp", "ws_id": "ws-sales-analytics", "role": "VIEWER"},
        "admin@globex.com": {"tenant_id": "tenant-globex", "org_id": "org-globex-intl", "ws_id": "ws-globex-eu", "role": "ORG_ADMIN"},
        "analyst@globex.com": {"tenant_id": "tenant-globex", "org_id": "org-globex-intl", "ws_id": "ws-globex-eu", "role": "ANALYST"},
    }

    if email_clean in DEMO_USERS and req.password == "password123":
        user_info = DEMO_USERS[email_clean]
        login_rate_limiter.record_success(email_clean)
        user_id = f"user-{email_clean.split('@')[0]}"
        token = create_access_token({
            "sub": user_id,
            "tenant_id": user_info["tenant_id"],
            "organization_id": user_info["org_id"],
            "workspace_id": user_info["ws_id"],
            "role": user_info["role"],
            "idp_provider": "local",
        })
        audit_logger.log_event(
            action="LOGIN_SUCCESS",
            resource=email_clean,
            result="ALLOWED",
            risk_level="LOW",
            reason=f"User authenticated successfully into tenant '{user_info['tenant_id']}'",
        )
        return LoginResponse(
            access_token=token,
            user_id=user_id,
            tenant_id=user_info["tenant_id"],
            role=user_info["role"],
            idp_provider="local",
        )

    # 3. Failed authentication attempt -> record and check threshold
    is_now_locked, fail_count, lock_time = login_rate_limiter.record_failure(email_clean)
    if is_now_locked:
        audit_logger.log_event(
            action="LOGIN_LOCKED_BRUTE_FORCE",
            resource=email_clean,
            result="BLOCKED",
            risk_level="CRITICAL",
            reason=f"Brute-force limit reached ({fail_count} failed attempts). Account locked for {lock_time}s.",
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many failed login attempts ({fail_count}/{login_rate_limiter.max_failed_attempts}). Account temporarily locked for {lock_time} seconds.",
            headers={"Retry-After": str(lock_time)},
        )

    remaining_tries = login_rate_limiter.max_failed_attempts - fail_count
    audit_logger.log_event(
        action="LOGIN_FAILED",
        resource=email_clean,
        result="BLOCKED",
        risk_level="MEDIUM",
        reason=f"Invalid credentials. Attempt {fail_count}/{login_rate_limiter.max_failed_attempts}.",
    )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Invalid email or password credentials. Remaining attempts before temporary lockout: {remaining_tries}.",
    )


@router.get("/sso/providers", response_model=List[SSOProviderInfo])
async def list_sso_providers():
    """
    Lists enterprise SSO / OIDC identity providers configured for federated authentication.
    """
    return [
        SSOProviderInfo(
            id="keycloak",
            name="Enterprise Keycloak SSO",
            protocol="OIDC",
            enabled=settings.ENABLE_OIDC_SSO,
            login_url=f"{settings.OIDC_ISSUER_URL}/protocol/openid-connect/auth?client_id={settings.OIDC_CLIENT_ID}&response_type=code&scope=openid%20profile%20email",
        ),
        SSOProviderInfo(
            id="okta",
            name="Corporate Okta Verify",
            protocol="SAML 2.0 / OIDC",
            enabled=settings.ENABLE_OIDC_SSO,
            login_url=f"https://enterprise.okta.com/app/{settings.OIDC_CLIENT_ID}/sso/saml",
        ),
        SSOProviderInfo(
            id="azure_ad",
            name="Microsoft Entra ID (Azure AD)",
            protocol="OIDC",
            enabled=settings.ENABLE_OIDC_SSO,
            login_url=f"https://login.microsoftonline.com/organizations/oauth2/v2.0/authorize?client_id={settings.OIDC_CLIENT_ID}&response_type=code",
        ),
    ]

from app.security.oidc import oidc_validator


@router.post("/sso/oidc/callback", response_model=LoginResponse)
async def oidc_callback(req: OIDCCallbackRequest):
    """
    Exchanges and cryptographically validates an OIDC ID Token from enterprise Identity Provider (IdP),
    enforces RS256 signature verification, maps enterprise claims (sub, tid, groups) to TenantContext,
    and issues platform JWT. Remediates Item 2.2 security vulnerability.
    """
    if not settings.ENABLE_OIDC_SSO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Enterprise SSO / OIDC is disabled by administrator policy.",
        )

    # Cryptographically verify ID token signature, expiration, and claims
    payload = oidc_validator.validate_id_token(req.id_token)

    extracted_email = payload.get("email", "sso.analyst@enterprise-corp.com")
    groups = payload.get("groups", [])
    if isinstance(groups, str):
        groups = [groups]

    extracted_role = "ANALYST"
    if any(g.lower() in ["admin", "org_admin", "org_admin_role", "administrators"] for g in groups) or "admin" in extracted_email.lower():
        extracted_role = "ORG_ADMIN"

    extracted_tenant = req.tenant_id or payload.get("tid", payload.get("tenant_id", "tenant-enterprise-sso"))
    raw_sub = payload.get("sub", extracted_email.split("@")[0])
    user_id = raw_sub if raw_sub.startswith("sso-") else f"sso-{raw_sub}"

    token = create_access_token({
        "sub": user_id,
        "tenant_id": extracted_tenant,
        "organization_id": payload.get("organization_id", "org-enterprise-sso"),
        "workspace_id": payload.get("workspace_id", "ws-corporate-analytics"),
        "role": extracted_role,
        "idp_provider": req.provider,
    })

    return LoginResponse(
        access_token=token,
        user_id=user_id,
        tenant_id=extracted_tenant,
        role=extracted_role,
        idp_provider=req.provider,
    )


@router.get("/me")
async def get_me(ctx: TenantContext = Depends(get_current_user_context)):
    return {
        "user_id": ctx.user_id,
        "tenant_id": ctx.tenant_id,
        "organization_id": ctx.organization_id,
        "workspace_id": ctx.workspace_id,
        "role": ctx.user_role,
        "authorized_regions": ctx.authorized_regions,
        "authorized_departments": ctx.authorized_departments,
    }
