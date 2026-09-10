from typing import Any, Dict, List, Optional

import sqlglot
from sqlglot import exp

from app.core.tenant import TenantContext


class SQLASTPolicyEngine:
    """
    Independent SQL Security Boundary using sqlglot AST parsing.
    Enforces SELECT-only operations and blocks DDL, DML, CTE bypasses, system calls,
    and provides structured AST diagnostics & compliance evaluation.
    """

    PROHIBITED_COMMANDS = (
        exp.Insert,
        exp.Update,
        exp.Delete,
        exp.Create,
        exp.Drop,
        exp.Alter,
        exp.Command,
    )

    PROHIBITED_TABLES = {
        "users",
        "passwords",
        "audit_logs",
        "ai_budgets",
        "secrets",
        "system_tables",
        "credentials",
    }
    PROHIBITED_FUNCTIONS = {
        "eval",
        "exec",
        "system",
        "pg_read_file",
        "load_extension",
        "install_extension",
        "copy",
        "read_blob",
        # DuckDB / SQLite file reading & export functions
        "read_csv",
        "read_csv_auto",
        "read_parquet",
        "read_json",
        "read_json_auto",
        "read_text",
        "scan_csv",
        "scan_parquet",
        "glob",
        "to_csv",
        "to_parquet",
        "write_csv",
        # DuckDB internal configuration, extension & secret table functions
        "duckdb_settings",
        "duckdb_secrets",
        "duckdb_extensions",
        "duckdb_memory",
        "duckdb_indexes",
        "duckdb_tables",
        "current_setting",
        "checkpoint",
        "attach",
        "detach",
    }

    PII_KEYWORDS = {"ssn", "credit_card", "password", "secret", "diagnosis", "medical_record"}

    def validate(self, sql_query: str, ctx: Optional[TenantContext] = None) -> Dict[str, Any]:
        if not sql_query or not sql_query.strip():
            return {"allowed": False, "reason": "Empty SQL query", "risk_level": "HIGH"}

        try:
            parsed = sqlglot.parse_one(sql_query)
        except Exception as e:
            return {
                "allowed": False,
                "reason": f"SQL Syntax Parse Error: {str(e)}",
                "risk_level": "HIGH",
            }

        # 1. Block multi-statement batches or blocks
        if isinstance(parsed, exp.Block):
            return {
                "allowed": False,
                "reason": "Multi-statement batch SQL queries are prohibited.",
                "risk_level": "CRITICAL",
            }

        # 2. Enforce analytical query root: SELECT, UNION, Subquery, Query
        if not isinstance(parsed, (exp.Select, exp.Union, exp.Subquery, exp.Query)):
            return {
                "allowed": False,
                "reason": "Destructive or non-analytical command detected. Only SELECT statements are permitted.",
                "risk_level": "CRITICAL",
            }

        # 3. Walk AST tree to block any destructive or file I/O node types
        for node in parsed.walk():
            node_type = type(node)
            if node_type in self.PROHIBITED_COMMANDS:
                return {
                    "allowed": False,
                    "reason": f"Prohibited operation '{node_type.__name__.upper()}' detected.",
                    "risk_level": "CRITICAL",
                }
            if getattr(exp, "ReadCSV", None) and isinstance(node, exp.ReadCSV):
                return {
                    "allowed": False,
                    "reason": "Prohibited file system access: 'read_csv' is not permitted.",
                    "risk_level": "CRITICAL",
                }
            if getattr(exp, "ReadParquet", None) and isinstance(node, exp.ReadParquet):
                return {
                    "allowed": False,
                    "reason": "Prohibited file system access: 'read_parquet' is not permitted.",
                    "risk_level": "CRITICAL",
                }

        # 4. Inspect all table references in AST
        tables_referenced = set()
        for table in parsed.find_all(exp.Table):
            table_name = table.name.lower()
            if table_name:
                tables_referenced.add(table_name)
                if table_name in self.PROHIBITED_TABLES:
                    return {
                        "allowed": False,
                        "reason": f"Access to system/restricted table '{table_name}' is prohibited.",
                        "risk_level": "CRITICAL",
                    }

        # 5. Block destructive or external access function calls
        for func in parsed.find_all(exp.Func):
            func_name = func.name.lower()
            if func_name in self.PROHIBITED_FUNCTIONS:
                return {
                    "allowed": False,
                    "reason": f"Prohibited SQL function '{func_name}' detected.",
                    "risk_level": "CRITICAL",
                }

        return {
            "allowed": True,
            "reason": "SQL AST Security Validation Passed",
            "risk_level": "LOW",
            "tables_referenced": list(tables_referenced),
        }

    def inspect_ast_structure(
        self, sql_query: str, compliance_mode: str = "SOC2"
    ) -> Dict[str, Any]:
        """
        Deeply inspects SQL AST nodes, extracts metadata, tables, projections, functions,
        and computes compliance readiness against standard policies (SOC2, HIPAA, PCI-DSS).
        """
        if not sql_query or not sql_query.strip():
            return {
                "is_valid_sql": False,
                "ast_tree": {},
                "risk_score": 100,
                "risk_level": "CRITICAL",
                "tables": [],
                "columns": [],
                "functions": [],
                "compliance_checklist": [],
                "violations": ["Query string is empty."],
            }

        violations: List[str] = []
        tables: List[str] = []
        columns: List[str] = []
        functions: List[str] = []
        is_analytical = False
        has_pii = False

        try:
            parsed = sqlglot.parse_one(sql_query)
            if isinstance(parsed, exp.Block):
                violations.append("Multi-statement batch SQL queries are forbidden.")
                is_analytical = False
            else:
                is_analytical = isinstance(parsed, (exp.Select, exp.Union, exp.Subquery, exp.Query))
        except Exception as e:
            return {
                "is_valid_sql": False,
                "ast_tree": {"type": "Error", "message": str(e)},
                "risk_score": 90,
                "risk_level": "HIGH",
                "tables": [],
                "columns": [],
                "functions": [],
                "compliance_checklist": [],
                "violations": [f"SQL Parsing Exception: {str(e)}"],
            }

        if not is_analytical:
            violations.append(
                "Non-analytical statement blocked: Data modification/DDL statements are forbidden."
            )

        for node in parsed.walk():
            node_type = type(node)
            if node_type in self.PROHIBITED_COMMANDS:
                violations.append(f"Prohibited operation '{node_type.__name__.upper()}' detected.")
            if getattr(exp, "ReadCSV", None) and isinstance(node, exp.ReadCSV):
                violations.append("Prohibited file system access: 'read_csv' is not permitted.")
            if getattr(exp, "ReadParquet", None) and isinstance(node, exp.ReadParquet):
                violations.append("Prohibited file system access: 'read_parquet' is not permitted.")

        for tbl in parsed.find_all(exp.Table):
            tname = tbl.name.lower()
            if tname:
                if tname not in tables:
                    tables.append(tname)
                if tname in self.PROHIBITED_TABLES:
                    violations.append(f"Restricted system table accessed: '{tname}'")

        for col in parsed.find_all(exp.Column):
            cname = col.name.lower()
            if cname not in columns:
                columns.append(cname)
            if cname in self.PII_KEYWORDS:
                has_pii = True

        for fn in parsed.find_all(exp.Func):
            fname = fn.name.lower()
            if fname not in functions:
                functions.append(fname)
            if fname in self.PROHIBITED_FUNCTIONS:
                violations.append(f"Prohibited native function call: '{fname}()'")

        # Simplified AST Tree structure for visualization
        ast_tree = {
            "root": parsed.key.upper() if hasattr(parsed, "key") else "SELECT",
            "projections": [str(exp_item) for exp_item in getattr(parsed, "expressions", [])][:8],
            "from_tables": tables,
            "where_clause": str(parsed.args.get("where")) if parsed.args.get("where") else None,
            "joins": [str(j) for j in getattr(parsed, "joins", [])][:4],
            "group_by": str(parsed.args.get("group")) if parsed.args.get("group") else None,
            "limit": str(parsed.args.get("limit")) if parsed.args.get("limit") else None,
        }

        # Compliance Evaluation Matrix
        compliance_checklist = [
            {
                "standard": "SOC2_TYPE_II",
                "rule": "Principle of Least Privilege (SELECT-only)",
                "passed": is_analytical and len(violations) == 0,
                "details": "Only analytical read-only queries are authorized.",
            },
            {
                "standard": "ISO27001",
                "rule": "System Credential & Audit Isolation",
                "passed": not any(t in self.PROHIBITED_TABLES for t in tables),
                "details": "Restricted authentication tables are safeguarded.",
            },
            {
                "standard": "HIPAA_PCI",
                "rule": "High-Risk Function & Shell Prevention",
                "passed": not any(f in self.PROHIBITED_FUNCTIONS for f in functions),
                "details": "Dangerous server-side command execution functions are blocked.",
            },
            {
                "standard": "GDPR_CCPA",
                "rule": "PII Exposure Verification",
                "passed": not has_pii,
                "details": "Unmasked direct PII identifier access detected."
                if has_pii
                else "No unmasked direct PII exposed.",
            },
        ]

        # Calculate numeric Risk Score (0 to 100)
        risk_score = 0
        if not is_analytical:
            risk_score += 85
        if any(t in self.PROHIBITED_TABLES for t in tables):
            risk_score += 30
        if any(f in self.PROHIBITED_FUNCTIONS for f in functions):
            risk_score += 25
        if has_pii:
            risk_score += 15

        risk_score = min(100, risk_score)
        risk_level = "LOW"
        if risk_score >= 70:
            risk_level = "CRITICAL"
        elif risk_score >= 35:
            risk_level = "HIGH"
        elif risk_score > 0:
            risk_level = "MEDIUM"

        return {
            "is_valid_sql": True,
            "is_safe": len(violations) == 0,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "ast_tree": ast_tree,
            "tables": tables,
            "columns": columns,
            "functions": functions,
            "has_pii": has_pii,
            "violations": violations,
            "compliance_checklist": compliance_checklist,
        }


ast_policy_engine = SQLASTPolicyEngine()
