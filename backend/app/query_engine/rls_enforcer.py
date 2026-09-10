from typing import Any, Dict, List, Optional, Tuple

import sqlglot
from sqlglot import exp

from app.core.tenant import TenantContext


class RowLevelSecurityEnforcer:
    """
    Independent RLS Security Rewriter using sqlglot AST transformation.
    Injects tenant isolation, regional, and departmental RLS predicates into queries,
    and maintains dynamic catalog-level governance policies.
    Remediates Item 2.1 (Mandatory RLS scope and catalog alignment).
    """

    # Backward-compatible static references
    TENANT_SCOPED_TABLES = {"orders", "customers"}
    REGION_SCOPED_TABLES = {"customers", "regions"}

    def __init__(self):
        # Dynamic Table -> Column Mappings for Multi-Tenant Row Isolation
        self.tenant_column_map: Dict[str, str] = {
            "orders": "tenant_id",
            "customers": "tenant_id",
        }
        # Dynamic Table -> Column Mappings for Regional RBAC
        self.region_column_map: Dict[str, str] = {
            "customers": "region",
            "regions": "region_name",
            "sales_orders": "region",
            "employee_performance": "region",
            "inventory_supply_chain": "region",
            "marketing_campaigns": "target_region",
        }
        # Dynamic Table -> Column Mappings for Departmental RBAC
        self.department_column_map: Dict[str, str] = {
            "employee_performance": "department",
            "financial_metrics": "department",
        }
        # Registered Public Benchmark Datasets (Single-Tenant Public Domain)
        self.public_benchmark_tables = {
            "olist_orders",
            "olist_order_items",
            "olist_products",
            "olist_customers",
            "olist_order_payments",
            "olist_order_reviews",
            "nyc_taxi_trips",
            "taxi_zones",
            "bts_flights",
            "bts_airlines",
            "bts_airports",
            "mimic_patients",
            "mimic_admissions",
            "mimic_icu_stays",
            "mimic_diagnoses",
            "chicago_crimes",
            "chicago_districts",
            "market_securities",
            "market_daily_prices",
            "market_financial_facts",
        }

    def register_tenant_policy(self, table_name: str, column_name: str = "tenant_id") -> None:
        """Dynamically registers a table under multi-tenant row isolation."""
        tbl = table_name.lower()
        self.tenant_column_map[tbl] = column_name
        self.TENANT_SCOPED_TABLES.add(tbl)

    def register_region_policy(self, table_name: str, column_name: str = "region") -> None:
        """Dynamically registers a table under regional RBAC scoping."""
        tbl = table_name.lower()
        self.region_column_map[tbl] = column_name
        self.REGION_SCOPED_TABLES.add(tbl)

    def register_department_policy(self, table_name: str, column_name: str = "department") -> None:
        """Dynamically registers a table under departmental RBAC scoping."""
        tbl = table_name.lower()
        self.department_column_map[tbl] = column_name

    def get_active_policies(self) -> Dict[str, Any]:
        """Returns active catalog-level RLS policies for security auditing."""
        return {
            "tenant_scoped": dict(self.tenant_column_map),
            "region_scoped": dict(self.region_column_map),
            "department_scoped": dict(self.department_column_map),
            "public_benchmark_tables": sorted(list(self.public_benchmark_tables)),
        }

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
            if tbl_name in self.tenant_column_map:
                col_name = self.tenant_column_map[tbl_name]
                tenant_col = exp.column(col_name, tbl_identifier)
                tenant_cond = exp.EQ(this=tenant_col, expression=exp.Literal.string(tenant_id))

                where = parsed.args.get("where")
                if where:
                    where.set("this", exp.and_(where.this, tenant_cond))
                else:
                    parsed = parsed.where(tenant_cond)

                injected_rules.append(
                    {
                        "type": "TENANT_ISOLATION",
                        "table": tbl_name,
                        "predicate": f"{tbl_identifier}.{col_name} = '{tenant_id}'",
                        "rationale": "Enforce strict tenant data boundary (Row-Level Security).",
                    }
                )

            # 2. Role-Based Attribute / Region Scoping (Non-Admin users on region-enabled tables)
            if user_role not in ("ORG_ADMIN", "SYSTEM_SUPERUSER"):
                if tbl_name in self.region_column_map and regions:
                    col_name = self.region_column_map[tbl_name]
                    region_col = exp.column(col_name, tbl_identifier)
                    region_literals = [exp.Literal.string(r) for r in regions]
                    region_cond = exp.In(this=region_col, expressions=region_literals)

                    where = parsed.args.get("where")
                    if where:
                        where.set("this", exp.and_(where.this, region_cond))
                    else:
                        parsed = parsed.where(region_cond)

                    injected_rules.append(
                        {
                            "type": "RBAC_REGION_SCOPE",
                            "table": tbl_name,
                            "predicate": f"{tbl_identifier}.{col_name} IN ({', '.join(repr(r) for r in regions)})",
                            "rationale": f"User role '{user_role}' is restricted to authorized regions: {regions}.",
                        }
                    )

                # 3. Departmental Scoping
                if tbl_name in self.department_column_map and authorized_departments:
                    dept_col_name = self.department_column_map[tbl_name]
                    dept_col = exp.column(dept_col_name, tbl_identifier)
                    dept_literals = [exp.Literal.string(d) for d in authorized_departments]
                    dept_cond = exp.In(this=dept_col, expressions=dept_literals)

                    where = parsed.args.get("where")
                    if where:
                        where.set("this", exp.and_(where.this, dept_cond))
                    else:
                        parsed = parsed.where(dept_cond)

                    injected_rules.append(
                        {
                            "type": "RBAC_DEPARTMENT_SCOPE",
                            "table": tbl_name,
                            "predicate": f"{tbl_identifier}.{dept_col_name} IN ({', '.join(repr(d) for d in authorized_departments)})",
                            "rationale": f"User role '{user_role}' is restricted to authorized departments: {authorized_departments}.",
                        }
                    )

            # 4. Public Benchmark Dataset Tracking (Audit note for unpartitioned open domains)
            if tbl_name in self.public_benchmark_tables and tbl_name not in self.tenant_column_map:
                injected_rules.append(
                    {
                        "type": "PUBLIC_DATASET_GOVERNANCE",
                        "table": tbl_name,
                        "predicate": "NONE (Public Read-Only Domain)",
                        "rationale": "Public benchmark dataset verified read-only AST without proprietary tenant partition.",
                    }
                )

        return parsed.sql(), injected_rules


rls_enforcer = RowLevelSecurityEnforcer()
