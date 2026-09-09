from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password, get_current_user_context
from app.core.tenant import TenantContext

router = APIRouter(prefix="/auth", tags=["Authentication"])


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
    # Seed demo authentication shortcut for enterprise demo users
    if req.email in ("analyst@acme.com", "admin@acme.com", "viewer@acme.com") and req.password == "password123":
        role = "ORG_ADMIN" if "admin" in req.email else ("VIEWER" if "viewer" in req.email else "ANALYST")
        token = create_access_token({
            "sub": f"user-{req.email.split('@')[0]}",
            "tenant_id": "tenant-acme",
            "organization_id": "org-acme-corp",
            "workspace_id": "ws-sales-analytics",
            "role": role,
            "idp_provider": "local",
        })
        return LoginResponse(
            access_token=token,
            user_id=f"user-{req.email.split('@')[0]}",
            tenant_id="tenant-acme",
            role=role,
            idp_provider="local",
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password credentials",
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
