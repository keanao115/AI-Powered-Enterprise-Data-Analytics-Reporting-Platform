import re
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from typing import Any, Dict, Optional

from app.core.config import settings
from app.core.database import analytics_adapter
from app.core.tenant import TenantContext, get_tenant_context
from app.query_engine.ast_policy import ast_policy_engine
from app.query_engine.column_masker import column_masker
from app.query_engine.cost_estimator import cost_estimator
from app.query_engine.rls_enforcer import rls_enforcer
from app.security.audit import audit_logger


class SecureQueryGateway:
    """
    Unified, Authoritative Security Gateway for Analytical SQL Execution.
    Guarantees Invariant 1: No SQL reaches the analytics engine without passing
    through this deterministic security boundary.

    Pipeline:
    1. Parse & AST Policy Validation (Blocks DDL/DML, file I/O, system tables, dangerous syntax)
    2. Role & Resource Authorization Check
    3. Logical Multi-Tenant & RBAC RLS Dynamic AST Rewriting
    4. Column-Level Security (CLS) Masking for PII/Sensitive Fields
    5. Cost Estimation & Cartesian Product Guardrails
    6. Resource Limits Enforcement (Wall-Clock Timeout & Row Limit Cap)
    7. Read-Only Database Execution
    8. Structured Security Audit Logging
    """

    def __init__(self):
        self._executor = ThreadPoolExecutor(
            max_workers=16, thread_name_prefix="secure_query_worker"
        )

    def execute(
        self,
        sql_query: str,
        ctx: Optional[TenantContext] = None,
        purpose: str = "analyst_query",
        timeout_seconds: Optional[int] = None,
        max_rows: Optional[int] = None,
        request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        start_time = time.time()

        # 0. Resolve or create tenant context
        if ctx is None:
            ctx = get_tenant_context()

        resolved_timeout = timeout_seconds or getattr(settings, "MAX_QUERY_SECONDS", 30)
        resolved_max_rows = max_rows or getattr(settings, "MAX_QUERY_ROWS", 10000)

        # 1. AST Policy Enforcement
        policy_res = ast_policy_engine.validate(sql_query, ctx)
        if not policy_res["allowed"]:
            audit_logger.log_event(
                action="SQL_BLOCKED",
                resource=sql_query,
                result="BLOCKED",
                risk_level="HIGH",
                reason=policy_res["reason"],
                ctx=ctx,
                request_id=request_id,
            )
            return {
                "success": False,
                "error": f"SQL Policy Denied: {policy_res['reason']}",
                "error_code": "SQL_POLICY_BLOCKED",
                "blocked": True,
                "execution_time_ms": round((time.time() - start_time) * 1000, 2),
            }

        # 2. Table & Operation Authorization
        # Normalize permissions for robust matching across string/enum and cases
        user_perms = {
            p.value.lower() if hasattr(p, "value") else str(p).lower().replace("_", ":")
            for p in (ctx.permissions if ctx else [])
        }
        user_perms.update({str(p).lower() for p in (ctx.permissions if ctx else [])})

        admin_roles = {"org_admin", "super_admin", "admin", "security_admin", "compliance_officer"}
        user_role_str = str(getattr(ctx, "user_role", "")).lower()
        has_admin_role = user_role_str in admin_roles or any(
            str(r).lower() in admin_roles for r in getattr(ctx, "roles", [])
        )

        has_query_perm = (
            "query:execute" in user_perms
            or "query_execute" in user_perms
            or "query:sql" in user_perms
            or "query_sql" in user_perms
            or has_admin_role
        )
        if not has_query_perm:
            audit_logger.log_event(
                action="AUTHORIZATION_DENIED",
                resource=sql_query,
                result="DENIED",
                risk_level="MEDIUM",
                reason="User lacks QUERY_EXECUTE permission",
                ctx=ctx,
                request_id=request_id,
            )
            return {
                "success": False,
                "error": "Authorization Denied: Insufficient permissions to execute analytical queries.",
                "error_code": "FORBIDDEN",
                "blocked": True,
                "execution_time_ms": round((time.time() - start_time) * 1000, 2),
            }

        # 3. Dynamic RLS AST Rewriting
        rewritten_sql, injected_rules = rls_enforcer.rewrite_with_persona(
            sql_query=sql_query,
            tenant_id=ctx.tenant_id if ctx else "default",
            user_role=ctx.user_role if ctx else "ANALYST",
            authorized_regions=ctx.authorized_regions if ctx else None,
            authorized_departments=ctx.authorized_departments if ctx else None,
        )

        # 4. Dynamic Column-Level Security (CLS) Masking
        cls_roles = {"security_admin", "dpo", "super_admin"}
        bypass_cls = (
            "data:restricted:read" in user_perms
            or "data_restricted_read" in user_perms
            or user_role_str in cls_roles
            or any(str(r).lower() in cls_roles for r in getattr(ctx, "roles", []))
        )
        masked_sql = rewritten_sql
        applied_masks = []
        if not bypass_cls:
            masked_sql, applied_masks = column_masker.apply_column_masking(
                rewritten_sql,
                user_role=ctx.user_role if ctx else "ANALYST",
            )

        # 5. Cost Estimation & Guardrails
        cost_eval = cost_estimator.estimate_cost(masked_sql)
        if (
            cost_eval.get("has_cartesian_product", False)
            and cost_eval.get("cost_rating") == "CRITICAL_OVERHEAD"
        ):
            audit_logger.log_event(
                action="QUERY_COST_BLOCKED",
                resource=masked_sql,
                result="BLOCKED",
                risk_level="MEDIUM",
                reason="Dangerous unconditioned Cartesian product detected without filters",
                ctx=ctx,
                request_id=request_id,
            )
            return {
                "success": False,
                "error": "Query Blocked by Cost Guardrail: Unconstrained Cartesian join detected.",
                "error_code": "COST_LIMIT_EXCEEDED",
                "blocked": True,
                "execution_time_ms": round((time.time() - start_time) * 1000, 2),
            }

        # 6. Row Limit Guardrail Cap
        final_sql = self._enforce_row_limit(masked_sql, resolved_max_rows)

        # 7. Read-Only Execution with Wall-Clock Timeout Enforcement
        try:
            future = self._executor.submit(analytics_adapter.execute_query, final_sql)
            res = future.result(timeout=resolved_timeout)
            execution_time_ms = (time.time() - start_time) * 1000

            # 8. Structured Security Audit Logging
            audit_logger.log_event(
                action="QUERY_EXECUTED",
                resource=final_sql,
                result="SUCCESS",
                risk_level="LOW",
                reason=f"Purpose: {purpose}, rows: {res.get('row_count', 0)}",
                ctx=ctx,
                request_id=request_id,
            )

            return {
                "success": True,
                "result": res,
                "final_sql": final_sql,
                "rls_injected_rules": injected_rules,
                "applied_masks": applied_masks,
                "execution_time_ms": round(execution_time_ms, 2),
                "cost_evaluation": cost_eval,
            }

        except FutureTimeoutError:
            execution_time_ms = (time.time() - start_time) * 1000
            audit_logger.log_event(
                action="QUERY_TIMEOUT_EXCEEDED",
                resource=final_sql,
                result="TIMEOUT",
                risk_level="HIGH",
                reason=f"Query exceeded max execution timeout of {resolved_timeout}s",
                ctx=ctx,
                request_id=request_id,
            )
            return {
                "success": False,
                "error": f"Query Execution Timed Out: Query exceeded maximum allowed execution time of {resolved_timeout} seconds.",
                "error_code": "QUERY_TIMEOUT",
                "execution_time_ms": round(execution_time_ms, 2),
            }

        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            audit_logger.log_event(
                action="QUERY_FAILED",
                resource=final_sql,
                result="ERROR",
                risk_level="LOW",
                reason=str(e),
                ctx=ctx,
                request_id=request_id,
            )
            return {
                "success": False,
                "error": str(e),
                "error_code": "EXECUTION_ERROR",
                "execution_time_ms": round(execution_time_ms, 2),
            }

    def _enforce_row_limit(self, sql: str, max_rows: int) -> str:
        """Ensures the SQL query has a LIMIT clause capped at max_rows."""
        sql_stripped = sql.strip().rstrip(";")
        limit_match = re.search(r"\bLIMIT\s+(\d+)", sql_stripped, re.IGNORECASE)
        if limit_match:
            existing_limit = int(limit_match.group(1))
            if existing_limit > max_rows:
                # Replace with capped limit
                sql_stripped = re.sub(
                    r"\bLIMIT\s+\d+",
                    f"LIMIT {max_rows}",
                    sql_stripped,
                    flags=re.IGNORECASE,
                )
            return sql_stripped
        else:
            return f"{sql_stripped} LIMIT {max_rows}"


secure_query_gateway = SecureQueryGateway()
