import time

from app.core.config import settings
from app.main import app
from app.security.oidc import oidc_validator
from fastapi.testclient import TestClient

client = TestClient(app)


def test_list_sso_providers():
    response = client.get("/api/v1/auth/sso/providers")
    assert response.status_code == 200
    providers = response.json()
    assert len(providers) >= 3
    ids = [p["id"] for p in providers]
    assert "keycloak" in ids
    assert "okta" in ids
    assert "azure_ad" in ids
    for p in providers:
        assert p["enabled"] is True
        assert "login_url" in p


def test_oidc_callback_cryptographic_verification():
    # 1. Valid cryptographically signed RS256 token
    mock_payload = {
        "sub": "sso-chief-analyst",
        "email": "chief.analyst@fortune500.com",
        "name": "Chief Analyst",
        "tid": "tenant-enterprise-global",
        "groups": ["analytics_team", "org_admin_role"],
        "iss": "https://iam.enterprise.internal/auth/realms/analytics",
        "aud": settings.OIDC_CLIENT_ID,
    }
    valid_id_token = oidc_validator.create_signed_test_token(mock_payload, expires_in_seconds=3600)

    response = client.post(
        "/api/v1/auth/sso/oidc/callback",
        json={
            "provider": "keycloak",
            "id_token": valid_id_token,
            "tenant_id": "tenant-enterprise-global",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["tenant_id"] == "tenant-enterprise-global"
    assert data["idp_provider"] == "keycloak"
    assert "chief-analyst" in data["user_id"]
    assert data["role"] == "ORG_ADMIN"

    # Verify that the generated platform token can access /auth/me
    token = data["access_token"]
    me_resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["tenant_id"] == "tenant-enterprise-global"


def test_oidc_callback_rejects_fake_signature():
    # 2. Forged signature vulnerability test (Remediates Item 2.2)
    # Tokens with fabricated payloads or '.fake_signature' must be strictly rejected with HTTP 401
    parts = oidc_validator.create_signed_test_token(
        {"sub": "attacker", "groups": ["org_admin"]}
    ).split(".")
    tampered_token = f"{parts[0]}.{parts[1]}.fake_signature_unauthorized"

    response = client.post(
        "/api/v1/auth/sso/oidc/callback",
        json={
            "provider": "keycloak",
            "id_token": tampered_token,
            "tenant_id": "tenant-enterprise-global",
        },
    )
    assert response.status_code == 401
    assert "signature verification failed" in response.json()["detail"].lower()


def test_oidc_callback_rejects_expired_token():
    # 3. Expired token rejection test
    mock_payload = {
        "sub": "sso-expired-user",
        "email": "user@fortune500.com",
        "exp": int(time.time()) - 3600,  # Expired 1 hour ago
        "aud": settings.OIDC_CLIENT_ID,
    }
    expired_token = oidc_validator.create_signed_test_token(mock_payload, expires_in_seconds=-3600)

    response = client.post(
        "/api/v1/auth/sso/oidc/callback",
        json={
            "provider": "okta",
            "id_token": expired_token,
        },
    )
    assert response.status_code == 401
    assert "expired" in response.json()["detail"].lower()


def test_oidc_callback_disabled_policy():
    # 4. Disabled SSO policy test
    original_state = settings.ENABLE_OIDC_SSO
    try:
        settings.ENABLE_OIDC_SSO = False
        response = client.post(
            "/api/v1/auth/sso/oidc/callback",
            json={
                "provider": "okta",
                "id_token": "some.token.value",
            },
        )
        assert response.status_code == 403
        assert "disabled" in response.json()["detail"].lower()
    finally:
        settings.ENABLE_OIDC_SSO = original_state
