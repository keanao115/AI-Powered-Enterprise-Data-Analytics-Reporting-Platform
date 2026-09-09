import pytest
import json
import base64
from fastapi.testclient import TestClient
from app.main import app

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


def test_oidc_callback_authentication():
    # Construct a mock JWT payload representing Keycloak / Okta ID token
    mock_payload = {
        "email": "chief.analyst@fortune500.com",
        "name": "Chief Analyst",
        "tid": "tenant-enterprise-global",
        "groups": ["analytics_team", "org_admin_role"],
        "iss": "https://iam.enterprise.internal/auth/realms/analytics",
    }
    encoded_payload = base64.urlsafe_b64encode(json.dumps(mock_payload).encode()).decode().rstrip("=")
    mock_id_token = f"eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.{encoded_payload}.fake_signature"

    response = client.post(
        "/api/v1/auth/sso/oidc/callback",
        json={
            "provider": "keycloak",
            "id_token": mock_id_token,
            "tenant_id": "tenant-enterprise-global"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["tenant_id"] == "tenant-enterprise-global"
    assert data["idp_provider"] == "keycloak"
    assert "sso-chief.analyst" in data["user_id"]

    # Verify that the generated token can access /auth/me
    token = data["access_token"]
    me_resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["tenant_id"] == "tenant-enterprise-global"
