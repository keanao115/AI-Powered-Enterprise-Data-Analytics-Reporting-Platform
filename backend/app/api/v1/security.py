from typing import List, Optional, Dict, Any
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.query_engine.ast_policy import ast_policy_engine
from app.query_engine.rls_enforcer import rls_enforcer
from app.query_engine.column_masker import column_masker
from app.query_engine.cost_estimator import cost_estimator

router = APIRouter(prefix="/security", tags=["SQL Security & Inspection"])


class SQLInspectRequest(BaseModel):
    raw_sql: str = Field(..., description="Raw candidate SQL query to inspect and simulate")
    simulated_tenant_id: str = Field(default="tenant-acme", description="Tenant ID to simulate")
    simulated_role: str = Field(default="ANALYST", description="User role to simulate")
    simulated_regions: List[str] = Field(default_factory=lambda: ["US", "EU"], description="Authorized regions")
    simulated_departments: List[str] = Field(default_factory=lambda: ["Sales"], description="Authorized departments")
    compliance_mode: str = Field(default="SOC2", description="Compliance standard to check (SOC2, HIPAA, PCI-DSS)")


class SQLInspectResponse(BaseModel):
    raw_sql: str
    rewritten_sql: str
    is_safe: bool
    risk_score: int
    risk_level: str
    violations: List[str]
    ast_analysis: Dict[str, Any]
    injected_predicates: List[Dict[str, Any]]
    masked_columns: List[Dict[str, Any]]
    cost_estimate: Dict[str, Any]
    compliance_checklist: List[Dict[str, Any]]
    mutation_explanations: List[str]


@router.post("/inspect-sql", response_model=SQLInspectResponse)
async def inspect_sql(req: SQLInspectRequest):
    raw_sql = req.raw_sql.strip()

    # 1. AST Structure & Compliance Analysis
    ast_result = ast_policy_engine.inspect_ast_structure(raw_sql, compliance_mode=req.compliance_mode)

    # 2. Dynamic Column-Level Security (CLS) Masking
    masked_sql, applied_masks = column_masker.apply_column_masking(
        sql_query=raw_sql,
        user_role=req.simulated_role
    )

    # 3. Dynamic Row-Level Security (RLS) Rewriting
    rewritten_sql, injected_rules = rls_enforcer.rewrite_with_persona(
        sql_query=masked_sql if ast_result["is_safe"] else raw_sql,
        tenant_id=req.simulated_tenant_id,
        user_role=req.simulated_role,
        authorized_regions=req.simulated_regions,
        authorized_departments=req.simulated_departments,
    )

    # 4. Performance & EXPLAIN Cost Estimation
    cost_data = cost_estimator.estimate_cost(rewritten_sql if ast_result["is_safe"] else raw_sql)

    # 5. Build Human-Readable Mutation Explanations
    mutation_explanations: List[str] = []
    for rule in injected_rules:
        if rule["type"] == "TENANT_ISOLATION":
            mutation_explanations.append(f"Injected tenant isolation on '{rule['table']}': {rule['predicate']}")
        elif rule["type"] == "RBAC_REGION_SCOPE":
            mutation_explanations.append(f"Applied region scope restriction for role '{req.simulated_role}': {rule['predicate']}")

    for mask in applied_masks:
        mutation_explanations.append(f"Dynamic PII masking applied to column '{mask['column']}' -> {mask['mask_applied']}")

    if not ast_result["is_safe"]:
        for v in ast_result["violations"]:
            mutation_explanations.append(f"[BLOCKED] Security Policy Violation: {v}")

    if not mutation_explanations and ast_result["is_safe"]:
        mutation_explanations.append("Query structure verified clean. No additional mutations required.")

    return SQLInspectResponse(
        raw_sql=raw_sql,
        rewritten_sql=rewritten_sql if ast_result["is_safe"] else "-- [BLOCKED BY SECURITY POLICY ENGINE]\n-- " + "\n-- ".join(ast_result["violations"]),
        is_safe=ast_result["is_safe"],
        risk_score=ast_result["risk_score"],
        risk_level=ast_result["risk_level"],
        violations=ast_result["violations"],
        ast_analysis=ast_result["ast_tree"],
        injected_predicates=injected_rules,
        masked_columns=applied_masks,
        cost_estimate=cost_data,
        compliance_checklist=ast_result["compliance_checklist"],
        mutation_explanations=mutation_explanations,
    )


@router.get("/presets")
async def get_security_presets():
    return [
        {
            "id": "preset-analytical",
            "name": "Standard Regional Sales Aggregation",
            "category": "ANALYTICAL",
            "sql": "SELECT region_name, SUM(amount) AS total_revenue FROM orders o JOIN regions r ON o.region_id = r.id GROUP BY region_name",
            "description": "Standard business analytics query. Evaluates multi-tenant isolation and region scoping."
        },
        {
            "id": "preset-pii",
            "name": "Customer Contact & SSN Extraction",
            "category": "PII_RESTRICTED",
            "sql": "SELECT name, email, phone, ssn, region FROM customers",
            "description": "Demonstrates Column-Level Security (CLS) dynamic masking on sensitive attributes."
        },
        {
            "id": "preset-destructive",
            "name": "Destructive DDL Injection (DROP TABLE)",
            "category": "MALICIOUS",
            "sql": "DROP TABLE customers; -- Attempted schema destruction",
            "description": "Demonstrates AST Policy Engine blocking non-SELECT DDL operations immediately."
        },
        {
            "id": "preset-costly",
            "name": "Unbounded Cartesian Cross-Join (High Cost)",
            "category": "PERFORMANCE_RISK",
            "sql": "SELECT * FROM orders, customers",
            "description": "Demonstrates performance guardrails detecting missing WHERE/JOIN clauses and Cartesian overhead."
        },
        {
            "id": "preset-sys-access",
            "name": "Restricted System Table Access",
            "category": "PRIVILEGE_ESCALATION",
            "sql": "SELECT * FROM users WHERE role = 'ADMIN'",
            "description": "Demonstrates blocking access to protected authentication and credentials tables."
        }
    ]
