import pytest
from app.main import app
from app.security.login_limiter import login_rate_limiter
from fastapi.testclient import TestClient

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_login_limiter():
    """Ensures clean slate for login rate limiter before each test."""
    login_rate_limiter.reset_all()
    yield
    login_rate_limiter.reset_all()


def test_successful_login_acme_and_globex():
    # 1. Acme Admin
    res1 = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@acme.com", "password": "password123"},
    )
    assert res1.status_code == 200
    d1 = res1.json()
    assert d1["tenant_id"] == "tenant-acme"
    assert d1["role"] == "ORG_ADMIN"
    assert "access_token" in d1

    # 2. Globex Analyst (Second Tenant)
    res2 = client.post(
        "/api/v1/auth/login",
        json={"email": "analyst@globex.com", "password": "password123"},
    )
    assert res2.status_code == 200
    d2 = res2.json()
    assert d2["tenant_id"] == "tenant-globex"
    assert d2["role"] == "ANALYST"
    assert "access_token" in d2


def test_failed_login_remaining_attempts_countdown():
    test_email = "target.user@acme.com"

    # Attempt 1
    r1 = client.post(
        "/api/v1/auth/login", json={"email": test_email, "password": "wrong_password_1"}
    )
    assert r1.status_code == 401
    assert "Remaining attempts before temporary lockout: 4" in r1.json()["detail"]

    # Attempt 2
    r2 = client.post(
        "/api/v1/auth/login", json={"email": test_email, "password": "wrong_password_2"}
    )
    assert r2.status_code == 401
    assert "Remaining attempts before temporary lockout: 3" in r2.json()["detail"]

    # Attempt 3
    r3 = client.post(
        "/api/v1/auth/login", json={"email": test_email, "password": "wrong_password_3"}
    )
    assert r3.status_code == 401
    assert "Remaining attempts before temporary lockout: 2" in r3.json()["detail"]

    # Attempt 4
    r4 = client.post(
        "/api/v1/auth/login", json={"email": test_email, "password": "wrong_password_4"}
    )
    assert r4.status_code == 401
    assert "Remaining attempts before temporary lockout: 1" in r4.json()["detail"]


def test_brute_force_lockout_trigger_at_threshold():
    test_email = "victim@acme.com"

    # 4 consecutive failures
    for i in range(4):
        resp = client.post(
            "/api/v1/auth/login", json={"email": test_email, "password": f"wrong_{i}"}
        )
        assert resp.status_code == 401

    # 5th failure -> triggers lockout (HTTP 429)
    resp5 = client.post("/api/v1/auth/login", json={"email": test_email, "password": "wrong_5"})
    assert resp5.status_code == 429
    assert "Account temporarily locked" in resp5.json()["detail"]
    assert "Retry-After" in resp5.headers

    # 6th attempt -> immediately blocked with HTTP 429
    resp6 = client.post("/api/v1/auth/login", json={"email": test_email, "password": "password123"})
    assert resp6.status_code == 429
    assert "Retry-After" in resp6.headers


def test_successful_login_resets_failure_count():
    test_email = "admin@acme.com"

    # 2 failures
    client.post("/api/v1/auth/login", json={"email": test_email, "password": "wrong_1"})
    client.post("/api/v1/auth/login", json={"email": test_email, "password": "wrong_2"})

    # 1 success
    res_succ = client.post(
        "/api/v1/auth/login", json={"email": test_email, "password": "password123"}
    )
    assert res_succ.status_code == 200

    # Next failure should have full 4 remaining attempts
    res_next = client.post(
        "/api/v1/auth/login", json={"email": test_email, "password": "wrong_again"}
    )
    assert res_next.status_code == 401
    assert "Remaining attempts before temporary lockout: 4" in res_next.json()["detail"]
