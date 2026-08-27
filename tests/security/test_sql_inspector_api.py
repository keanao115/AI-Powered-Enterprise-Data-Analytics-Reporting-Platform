import pytest
from app.query_engine.ast_policy import ast_policy_engine
from app.query_engine.rls_enforcer import rls_enforcer
from app.query_engine.column_masker import column_masker
from app.query_engine.cost_estimator import cost_estimator


def test_ast_policy_deep_inspection():
    safe_sql = "SELECT region_name, SUM(amount) FROM orders o JOIN regions r ON o.region_id = r.id GROUP BY region_name"
    res = ast_policy_engine.inspect_ast_structure(safe_sql, compliance_mode="SOC2")
    assert res["is_valid_sql"] is True
    assert res["is_safe"] is True
    assert res["risk_level"] == "LOW"
    assert "orders" in res["tables"]

    malicious_sql = "DROP TABLE customers; -- destructive test"
    res_mal = ast_policy_engine.inspect_ast_structure(malicious_sql, compliance_mode="SOC2")
    assert res_mal["is_safe"] is False
    assert res_mal["risk_level"] == "CRITICAL"
    assert len(res_mal["violations"]) > 0


def test_column_level_security_masking():
    pii_sql = "SELECT name, email, ssn, phone FROM customers"
    masked_sql, applied_masks = column_masker.apply_column_masking(pii_sql, user_role="ANALYST")
    
    assert len(applied_masks) >= 3
    assert "RIGHT(ssn, 4)" in masked_sql
    assert "***@" in masked_sql

    # DPO bypass test
    bypass_sql, bypass_masks = column_masker.apply_column_masking(pii_sql, user_role="DPO")
    assert len(bypass_masks) == 0
    assert bypass_sql == pii_sql


def test_rls_persona_simulation():
    raw_sql = "SELECT region, COUNT(id) FROM customers GROUP BY region"
    rewritten_sql, injected_rules = rls_enforcer.rewrite_with_persona(
        sql_query=raw_sql,
        tenant_id="tenant-globex",
        user_role="ANALYST",
        authorized_regions=["EU", "APAC"]
    )

    assert "tenant_id = 'tenant-globex'" in rewritten_sql
    assert "region IN ('EU', 'APAC')" in rewritten_sql
    assert len(injected_rules) >= 2


def test_cost_estimator_and_guardrails():
    # Normal query
    normal_sql = "SELECT * FROM orders WHERE tenant_id = 'tenant-acme' LIMIT 10"
    cost_res = cost_estimator.estimate_cost(normal_sql)
    assert "estimated_rows" in cost_res
    assert cost_res["has_cartesian_product"] is False

    # Cartesian Product
    cartesian_sql = "SELECT * FROM orders, customers"
    cart_res = cost_estimator.estimate_cost(cartesian_sql)
    assert cart_res["has_cartesian_product"] is True
    assert cart_res["cost_rating"] == "CRITICAL_OVERHEAD"
