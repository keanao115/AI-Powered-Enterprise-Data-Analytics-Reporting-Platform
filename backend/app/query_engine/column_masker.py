import sqlglot
from sqlglot import exp
from typing import Dict, Any, List, Tuple, Set


class ColumnLevelSecurityMasker:
    """
    Column-Level Security (CLS) Engine using SQL AST manipulation.
    Detects and dynamically rewrites projection expressions for PII and sensitive columns.
    """

    RESTRICTED_COLUMNS_CONFIG: Dict[str, Dict[str, Any]] = {
        "ssn": {
            "type": "SSN",
            "sensitivity": "RESTRICTED",
            "replacement": "CONCAT('***-**-', RIGHT({col}, 4))",
        },
        "email": {
            "type": "EMAIL",
            "sensitivity": "CONFIDENTIAL",
            "replacement": "CONCAT(LEFT({col}, 2), '***@***.com')",
        },
        "phone": {
            "type": "PHONE",
            "sensitivity": "CONFIDENTIAL",
            "replacement": "CONCAT('***-***-', RIGHT({col}, 4))",
        },
        "credit_card": {
            "type": "CARD_NUMBER",
            "sensitivity": "RESTRICTED",
            "replacement": "CONCAT('****-****-****-', RIGHT({col}, 4))",
        },
        "password": {
            "type": "CREDENTIAL",
            "sensitivity": "RESTRICTED",
            "replacement": "'[REDACTED_SECRET]'",
        },
        "diagnosis": {
            "type": "HEALTH_DATA",
            "sensitivity": "RESTRICTED",
            "replacement": "CONCAT(LEFT({col}, 3), '***')",
        },
    }

    def apply_column_masking(
        self,
        sql_query: str,
        user_role: str = "ANALYST",
        bypass_roles: Set[str] = None
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Rewrites the SQL AST to mask sensitive columns in SELECT projection expressions.
        Returns: (masked_sql, list_of_applied_masks)
        """
        if bypass_roles is None:
            bypass_roles = {"DPO", "SECURITY_ADMIN"}

        # If user has security admin/DPO clearance, bypass dynamic masking
        if user_role in bypass_roles:
            return sql_query, []

        try:
            parsed = sqlglot.parse_one(sql_query)
        except Exception:
            return sql_query, []

        if not isinstance(parsed, exp.Select):
            return sql_query, []

        applied_masks: List[Dict[str, Any]] = []

        # Inspect and rewrite SELECT expressions
        new_select_expressions = []
        for select_expr in parsed.expressions:
            col_name = ""
            alias_name = None

            if isinstance(select_expr, exp.Column):
                col_name = select_expr.name.lower()
                alias_name = select_expr.alias or select_expr.name
            elif isinstance(select_expr, exp.Alias):
                if isinstance(select_expr.this, exp.Column):
                    col_name = select_expr.this.name.lower()
                    alias_name = select_expr.alias

            if col_name in self.RESTRICTED_COLUMNS_CONFIG:
                cfg = self.RESTRICTED_COLUMNS_CONFIG[col_name]
                raw_expr_str = cfg["replacement"].format(col=col_name)
                
                # Parse replacement SQL snippet into sqlglot expression
                mask_ast = sqlglot.parse_one(raw_expr_str)
                aliased_mask = exp.alias_(mask_ast, alias_name or col_name)
                new_select_expressions.append(aliased_mask)

                applied_masks.append({
                    "column": col_name,
                    "sensitivity": cfg["sensitivity"],
                    "data_type": cfg["type"],
                    "mask_applied": raw_expr_str,
                    "target_alias": alias_name or col_name,
                })
            else:
                new_select_expressions.append(select_expr)

        parsed.set("expressions", new_select_expressions)
        return parsed.sql(), applied_masks


column_masker = ColumnLevelSecurityMasker()
