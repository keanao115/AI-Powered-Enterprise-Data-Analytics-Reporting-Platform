from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
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
        })
        return LoginResponse(
            access_token=token,
            user_id=f"user-{req.email.split('@')[0]}",
            tenant_id="tenant-acme",
            role=role,
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password credentials",
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
