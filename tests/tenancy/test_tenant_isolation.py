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
