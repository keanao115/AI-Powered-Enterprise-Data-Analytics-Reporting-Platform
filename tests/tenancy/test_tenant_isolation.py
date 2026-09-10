import pytest
from app.sandbox.code_validator import code_validator
from app.sandbox.runner import sandbox_runner
from app.security.tenant_isolation import tenant_isolation
from app.core.tenant import TenantContext
from app.core.exceptions import TenantAccessDeniedException


def test_sandbox_code_validator():
    # 1. Block prohibited modules & system functions
    dangerous_codes = [
        "import os; os.system('whoami')",
        "import sys; sys.exit(1)",
        "import subprocess; subprocess.run(['ls', '-la'])",
        "import socket; s = socket.socket()",
        "eval('__import__(\"os\").system(\"id\")')",
    ]
    for code in dangerous_codes:
        is_safe, reason = code_validator.validate(code)
        assert not is_safe, f"Failed to block dangerous Python code: {code}"

    # 2. Allow standard pandas / numpy / matplotlib statistical code
    safe_code = """
import pandas as pd
import numpy as np

df = pd.DataFrame(data['rows'], columns=data['columns'])
result = {'mean_revenue': float(df['amount'].mean())}
"""
    is_safe, _ = code_validator.validate(safe_code)
    assert is_safe


def test_sandbox_runner_execution():
    code = """
import pandas as pd
df = pd.DataFrame(data['rows'], columns=data['columns'])
result = {'sum': int(df['amount'].sum())}
"""
    data = {"columns": ["amount"], "rows": [[100], [200], [300]]}
    res = sandbox_runner.run_code(code, data)
    assert res["success"]
    assert res["result"]["sum"] == 600


def test_tenant_isolation_enforcement():
    ctx_a = TenantContext(
        tenant_id="tenant-a",
        organization_id="org-a",
        workspace_id="ws-a",
        user_id="user-a",
        user_role="ANALYST",
        authorized_regions=["US"],
        authorized_departments=["Sales"],
    )

    # Authorized same-tenant access
    assert tenant_isolation.validate_tenant_access("tenant-a", ctx_a)

    # Cross-tenant access attempt must raise TenantAccessDeniedException
    with pytest.raises(TenantAccessDeniedException):
        tenant_isolation.validate_tenant_access("tenant-b", ctx_a)


def test_cross_tenant_data_isolation_between_acme_and_globex():
    """
    Remediates Item 2.1: Proves multi-tenant RLS isolation with multiple distinct tenants
    (tenant-acme vs tenant-globex) in synthetic database.
    """
    from app.query_engine.rls_enforcer import rls_enforcer
    from app.query_engine.executor import query_executor

    # 1. Verify raw database has total records across all tenants
    raw_cust_res = query_executor.execute("SELECT COUNT(*) AS total FROM customers")
    assert raw_cust_res["success"] is True
    total_raw_customers = int(raw_cust_res["result"]["rows"][0][0])
    assert total_raw_customers == 7  # 4 Acme + 3 Globex

    raw_ord_res = query_executor.execute("SELECT COUNT(*) AS total FROM orders")
    assert raw_ord_res["success"] is True
    total_raw_orders = int(raw_ord_res["result"]["rows"][0][0])
    assert total_raw_orders == 9  # 6 Acme + 3 Globex

    # 2. Context A: Tenant Acme (All authorized regions)
    query = "SELECT id, name, email FROM customers"
    rewritten_acme, rules_acme = rls_enforcer.rewrite_with_persona(
        sql_query=query,
        tenant_id="tenant-acme",
        user_role="ANALYST",
        authorized_regions=["US", "EU", "APAC"],
    )
    assert "tenant-acme" in rewritten_acme
    res_acme = query_executor.execute(rewritten_acme)
    assert res_acme["success"] is True
    acme_rows = res_acme["result"]["rows"]
    assert len(acme_rows) == 4  # Strictly only Acme's 4 customers across all regions
    acme_emails = [r[2] for r in acme_rows]
    assert "admin@acme.com" in acme_emails
    assert "ops@globex.eu" not in acme_emails  # Zero leakage of Globex data!

    # 3. Context B: Tenant Globex (All authorized regions)
    rewritten_globex, rules_globex = rls_enforcer.rewrite_with_persona(
        sql_query=query,
        tenant_id="tenant-globex",
        user_role="ANALYST",
        authorized_regions=["US", "EU", "APAC"],
    )
    assert "tenant-globex" in rewritten_globex
    res_globex = query_executor.execute(rewritten_globex)
    assert res_globex["success"] is True
    globex_rows = res_globex["result"]["rows"]
    assert len(globex_rows) == 3  # Strictly only Globex's 3 customers across all regions
    globex_emails = [r[2] for r in globex_rows]
    assert "ops@globex.eu" in globex_emails
    assert "admin@acme.com" not in globex_emails  # Zero leakage of Acme data!

    # 4. Cross-tenant order counts (using ORG_ADMIN role for unconstrained regional view)
    order_query = "SELECT COUNT(*) as cnt, SUM(amount) as total FROM orders"
    rewritten_acme_ord, _ = rls_enforcer.rewrite_with_persona(order_query, tenant_id="tenant-acme", user_role="ORG_ADMIN")
    res_acme_ord = query_executor.execute(rewritten_acme_ord)
    assert int(res_acme_ord["result"]["rows"][0][0]) == 6  # Acme has 6 orders

    rewritten_globex_ord, _ = rls_enforcer.rewrite_with_persona(order_query, tenant_id="tenant-globex", user_role="ORG_ADMIN")
    res_globex_ord = query_executor.execute(rewritten_globex_ord)
    assert int(res_globex_ord["result"]["rows"][0][0]) == 3  # Globex has 3 orders

