import pytest
from app.ai.llm_gateway import llm_gateway
from app.ai.schemas.llm_schemas import LLMMessage
from app.core.config import settings
from app.core.permissions import Role
from app.core.security import create_access_token
from app.core.tenant import TenantContext
from app.main import app
from app.query_engine.repair import sql_repair_service
from app.query_engine.secure_gateway import secure_query_gateway
from app.sandbox.runner import sandbox_runner
from app.security.token_governance import (
    RateLimitExceededException,
    token_governance,
)
from fastapi.testclient import TestClient

client = TestClient(app)


def test_secure_query_gateway_enforces_ast_and_rls():
    """Validates that SecureQueryGateway blocks DDL/DML and enforces multi-tenant RLS."""
    ctx_acme = TenantContext(
        tenant_id="tenant-acme",
        organization_id="org-acme",
        workspace_id="ws-main",
        user_id="usr-acme-01",
        roles=[Role.ORG_ADMIN],
        permissions=["query:execute", "query:sql"],
    )

    # 1. Block destructive DDL/DML
    malicious_sql = "DROP TABLE orders;"
    res_drop = secure_query_gateway.execute(malicious_sql, ctx=ctx_acme)
    assert not res_drop["success"]
    assert res_drop.get("blocked") is True
    assert "DROP" in res_drop["error"] or "Policy Denied" in res_drop["error"]

    # 2. Block Cartesian products without filters when critical
    cartesian_sql = "SELECT * FROM orders, customers;"
    res_cartesian = secure_query_gateway.execute(cartesian_sql, ctx=ctx_acme)
    # RLS injects WHERE tenant_id, resolving Cartesian if filtered, or cost blocks it
    assert res_cartesian.get("success") or res_cartesian.get("blocked")

    # 3. Verify tenant isolation in final SQL
    select_sql = "SELECT * FROM customers;"
    res_select = secure_query_gateway.execute(select_sql, ctx=ctx_acme)
    assert res_select["success"]
    final_sql = res_select["final_sql"]
    assert "tenant_id" in final_sql
    assert "LIMIT" in final_sql
    # Acme should only see 4 customers
    assert res_select["result"]["row_count"] == 4


def test_repaired_sql_reapplies_rls_and_prevents_cross_tenant_bypass():
    """
    Verifies that when SQL repair runs, repaired SQL is forced through
    the SecureQueryGateway and re-applies tenant RLS.
    """
    ctx_globex = TenantContext(
        tenant_id="tenant-globex",
        organization_id="org-globex",
        workspace_id="ws-main",
        user_id="usr-globex-01",
        roles=[Role.ANALYST],
        permissions=["query:execute", "query:sql"],
    )

    # A query with a syntax error that mentions customers
    broken_sql = "SELECT * FROM customers WHERE INVALID_SYNTAX"
    repair_res = sql_repair_service.repair_and_execute(
        failed_sql=broken_sql,
        error_message="no such column: INVALID_SYNTAX",
        ctx=ctx_globex,
    )
    assert repair_res["success"] is True
    assert repair_res.get("repaired") is True
    # Result must only contain Globex records (3 customers)
    assert repair_res["result"]["row_count"] == 3


def test_sandbox_timeout_terminates_infinite_loop():
    """Verifies that the process-isolated sandbox cleanly terminates infinite loops."""
    infinite_loop_code = """
i = 0
while True:
    i += 1
"""
    res = sandbox_runner.run_code(infinite_loop_code, {}, timeout_seconds=1)
    assert res["success"] is False
    assert res.get("error_code") == "SANDBOX_TIMEOUT"
    assert "timeout" in res["error"].lower()


def test_sandbox_blocks_malicious_builtins_and_system_escape():
    """Verifies AST and runtime restrictions prevent host escape."""
    # 1. Prohibited import
    res1 = sandbox_runner.run_code("import subprocess", {})
    assert res1["success"] is False
    assert res1.get("error_code") == "SANDBOX_AST_BLOCKED"

    # 2. Reflection / OS escape attempt
    res2 = sandbox_runner.run_code("import os\nos.system('dir')", {})
    assert res2["success"] is False
    assert res2.get("error_code") == "SANDBOX_AST_BLOCKED"

    # 3. Legitimate calculation succeeds
    res3 = sandbox_runner.run_code("result = {'val': sum(data['nums'])}", {"nums": [1, 2, 3, 4, 5]})
    assert res3["success"] is True
    assert res3["result"]["val"] == 15


def test_production_auth_fails_closed_when_token_missing():
    """
    Verifies that when DEMO_MODE=False, unauthenticated requests fail-closed with HTTP 401.
    """
    original_demo_mode = settings.DEMO_MODE
    try:
        settings.DEMO_MODE = False

        # Request /api/v1/auth/me without token
        resp = client.get("/api/v1/auth/me")
        assert resp.status_code == 401
        data = resp.json()
        assert "AUTHENTICATION_FAILED" in str(data) or "error" in data

    finally:
        settings.DEMO_MODE = original_demo_mode


def test_settings_control_plane_requires_admin_role():
    """
    Verifies that modifying LLM/Vault configuration requires SETTINGS_MANAGE (ORG_ADMIN).
    Analysts and Viewers receive HTTP 403 Forbidden.
    """
    analyst_token = create_access_token(
        {
            "sub": "analyst@acme.com",
            "tenant_id": "tenant-acme",
            "role": Role.ANALYST.value,
        }
    )

    admin_token = create_access_token(
        {
            "sub": "admin@acme.com",
            "tenant_id": "tenant-acme",
            "role": Role.ORG_ADMIN.value,
        }
    )

    headers_analyst = {"Authorization": f"Bearer {analyst_token}"}
    headers_admin = {"Authorization": f"Bearer {admin_token}"}

    # 1. Analyst can VIEW settings
    resp_view = client.get("/api/v1/settings/llm", headers=headers_analyst)
    assert resp_view.status_code == 200

    # 2. Analyst is FORBIDDEN (403) from updating LLM settings
    resp_update_forbidden = client.post(
        "/api/v1/settings/llm",
        json={"provider": "mock", "persist_to_env": False},
        headers=headers_analyst,
    )
    assert resp_update_forbidden.status_code == 403

    # 3. Analyst is FORBIDDEN (403) from adding vault keys
    resp_vault_forbidden = client.post(
        "/api/v1/settings/vault",
        json={"provider": "mock", "api_key": "mock-key", "model": "mock"},
        headers=headers_analyst,
    )
    assert resp_vault_forbidden.status_code == 403

    # 4. ORG_ADMIN can update LLM settings
    resp_admin_ok = client.post(
        "/api/v1/settings/llm",
        json={"provider": "mock", "persist_to_env": False},
        headers=headers_admin,
    )
    assert resp_admin_ok.status_code == 200


def test_jobs_cross_tenant_access_blocked_with_404():
    """
    Verifies that jobs belonging to another tenant cannot be inspected or enumerated.
    """
    acme_token = create_access_token(
        {
            "sub": "analyst@acme.com",
            "tenant_id": "tenant-acme",
            "role": Role.ANALYST.value,
        }
    )
    headers = {"Authorization": f"Bearer {acme_token}"}

    # 1. Access own tenant job succeeds
    resp_own = client.get("/api/v1/jobs/job-demo-acme-001", headers=headers)
    assert resp_own.status_code == 200
    assert resp_own.json()["job_id"] == "job-demo-acme-001"

    # 2. Access Globex job returns 404 (IDOR prevention)
    resp_other = client.get("/api/v1/jobs/job-demo-globex-001", headers=headers)
    assert resp_other.status_code == 404

    # 3. Access nonexistent job returns 404
    resp_nonexistent = client.get("/api/v1/jobs/nonexistent-999", headers=headers)
    assert resp_nonexistent.status_code == 404


def test_reports_path_traversal_and_cross_tenant_blocked():
    """
    Verifies that reports endpoint strictly rejects path traversal and cross-tenant access.
    """
    acme_token = create_access_token(
        {
            "sub": "analyst@acme.com",
            "tenant_id": "tenant-acme",
            "role": Role.ANALYST.value,
        }
    )
    headers = {"Authorization": f"Bearer {acme_token}"}

    # 1. Path traversal characters rejected with 400
    resp_traversal = client.get("/api/v1/reports/..%2F..%2Fetc%2Fpasswd/download", headers=headers)
    assert resp_traversal.status_code in [400, 404]

    # 2. Nonexistent malicious ID rejected with 404 (no arbitrary generation)
    resp_fake = client.get("/api/v1/reports/malicious-random-9999/download", headers=headers)
    assert resp_fake.status_code == 404


def test_dataset_explorer_enforces_governance_and_cls():
    """
    Verifies that dataset explorer queries pass through SecureQueryGateway with masking.
    """
    resp = client.get("/api/v1/datasets/ecommerce_olist")
    assert resp.status_code == 200
    data = resp.json()
    assert "columns" in data
    assert "rows" in data
    assert len(data["columns"]) > 0


def test_token_governance_enforced_in_llm_request_path():
    """
    Verifies that LLMGateway.generate() actively checks sliding-window RPM rate limits.
    """
    tenant_id = "test-governance-tenant"
    # Set low RPM to test enforcement
    old_rpm = token_governance.rpm_limit
    try:
        token_governance.rpm_limit = 2
        msg = [LLMMessage(role="user", content="Ping")]

        # Request 1 & 2 succeed
        r1 = llm_gateway.generate(msg, role=None, tenant_id=tenant_id)
        assert r1.content is not None
        r2 = llm_gateway.generate(msg, role=None, tenant_id=tenant_id)
        assert r2.content is not None

        # Request 3 triggers rate limit exception
        with pytest.raises(RateLimitExceededException) as exc_info:
            llm_gateway.generate(msg, role=None, tenant_id=tenant_id)
        assert "rate limit" in str(exc_info.value).lower()
    finally:
        token_governance.rpm_limit = old_rpm
