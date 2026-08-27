import sqlglot
from sqlglot import exp
from typing import Optional, List, Tuple, Dict, Any
from app.core.tenant import TenantContext


class RowLevelSecurityEnforcer:
    """
    Independent RLS Security Rewriter using sqlglot AST transformation.
    Injects tenant isolation and region/department RLS predicates into generated queries.
    """

    TENANT_SCOPED_TABLES = {"orders", "customers"}
    REGION_SCOPED_TABLES = {"customers", "regions"}

    def apply_rls_predicates(self, sql_query: str, ctx: TenantContext) -> str:
        rewritten_sql, _ = self.rewrite_with_persona(
            sql_query=sql_query,
            tenant_id=ctx.tenant_id,
            user_role=ctx.user_role,
            authorized_regions=ctx.authorized_regions,
            authorized_departments=ctx.authorized_departments,
        )
        return rewritten_sql

    def rewrite_with_persona(
        self,
        sql_query: str,
        tenant_id: str = "tenant-acme",
        user_role: str = "ANALYST",
        authorized_regions: Optional[List[str]] = None,
        authorized_departments: Optional[List[str]] = None,
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Dynamically applies RLS predicates based on simulated persona attributes.
        Returns: (rewritten_sql, list_of_injected_rules)
        """
        try:
            parsed = sqlglot.parse_one(sql_query)
        except Exception:
            return sql_query, []

        if not isinstance(parsed, exp.Select):
            return sql_query, []

        injected_rules: List[Dict[str, Any]] = []
        regions = authorized_regions or ["US", "EU"]

        # Traverse all tables in SELECT query
        for table in parsed.find_all(exp.Table):
            tbl_name = table.name.lower()
            tbl_identifier = table.alias if table.alias else table.name

            # 1. Mandatory Multi-Tenant Row Isolation
            if tbl_name in self.TENANT_SCOPED_TABLES:
                tenant_col = exp.column("tenant_id", tbl_identifier)
                tenant_cond = exp.EQ(this=tenant_col, expression=exp.Literal.string(tenant_id))

                where = parsed.args.get("where")
                if where:
                    where.set("this", exp.and_(where.this, tenant_cond))
                else:
                    parsed = parsed.where(tenant_cond)

                injected_rules.append({
                    "type": "TENANT_ISOLATION",
                    "table": tbl_name,
                    "predicate": f"{tbl_identifier}.tenant_id = '{tenant_id}'",
                    "rationale": "Enforce strict tenant data boundary (Row-Level Security)."
                })

            # 2. Role-Based Attribute / Region Scoping (Non-Admin users on region-enabled tables)
            if user_role not in ("ORG_ADMIN", "SYSTEM_SUPERUSER"):
                if tbl_name in self.REGION_SCOPED_TABLES and regions:
                    region_col = exp.column("region_name", tbl_identifier) if tbl_name == "regions" else exp.column("region", tbl_identifier)
                    region_literals = [exp.Literal.string(r) for r in regions]
                    region_cond = exp.In(this=region_col, expressions=region_literals)

                    where = parsed.args.get("where")
                    if where:
                        where.set("this", exp.and_(where.this, region_cond))
                    else:
                        parsed = parsed.where(region_cond)

                    injected_rules.append({
                        "type": "RBAC_REGION_SCOPE",
                        "table": tbl_name,
                        "predicate": f"{tbl_identifier}.{region_col.name} IN ({', '.join(repr(r) for r in regions)})",
                        "rationale": f"User role '{user_role}' is restricted to authorized regions: {regions}."
                    })

        return parsed.sql(), injected_rules


rls_enforcer = RowLevelSecurityEnforcer()
