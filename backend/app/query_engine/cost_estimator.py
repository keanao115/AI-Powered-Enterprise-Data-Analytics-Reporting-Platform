import re
import duckdb
import sqlglot
from sqlglot import exp
from typing import Dict, Any, List
from app.core.database import get_analytics_db_path


class QueryPerformanceCostEstimator:
    """
    Evaluates SQL execution cost, AST query complexity, and generates EXPLAIN plan insights.
    Acts as a performance guardrail against unbounded scans and Cartesian products.
    """

    MAX_ESTIMATED_ROWS_THRESHOLD = 500_000

    def estimate_cost(self, sql_query: str) -> Dict[str, Any]:
        warnings: List[str] = []
        is_cost_exceeded = False
        has_cartesian_product = False
        tables_involved: List[str] = []
        join_count = 0
        has_where_clause = False

        # 1. Static AST Complexity Analysis
        try:
            parsed = sqlglot.parse_one(sql_query)
            if isinstance(parsed, exp.Select):
                tables_involved = [t.name.lower() for t in parsed.find_all(exp.Table)]
                joins = list(parsed.find_all(exp.Join))
                join_count = len(joins)
                has_where_clause = parsed.args.get("where") is not None

                # Detect potential Cartesian Product (Multiple tables without JOIN or with unconditioned/CROSS joins)
                has_unconditioned_join = any(j.args.get("on") is None for j in joins) if joins else False
                if len(tables_involved) > 1 and (join_count == 0 or has_unconditioned_join) and not has_where_clause:
                    has_cartesian_product = True
                    warnings.append("Cartesian product detected: multiple tables referenced without JOIN condition or filter.")
        except Exception:
            pass

        # 2. Database EXPLAIN Plan Analysis
        explain_raw = ""
        estimated_rows = 1000
        plan_nodes: List[Dict[str, Any]] = []

        try:
            db_path = get_analytics_db_path()
            conn = duckdb.connect(db_path, read_only=True)
            
            # Execute EXPLAIN query
            explain_res = conn.execute(f"EXPLAIN {sql_query}").fetchall()
            conn.close()

            explain_lines = [row[1] for row in explain_res if len(row) > 1]
            explain_raw = "\n".join(explain_lines)

            # Parse DuckDB explain plan text
            for line in explain_lines:
                if "SCAN" in line.upper() or "FILTER" in line.upper() or "JOIN" in line.upper() or "PROJECTION" in line.upper():
                    plan_nodes.append({
                        "operation": line.strip(),
                        "type": "SCAN" if "SCAN" in line.upper() else ("JOIN" if "JOIN" in line.upper() else "TRANSFORM")
                    })

                # Extract Estimated cardinality / rows if available
                row_match = re.search(r"EC:\s*(\d+)", line)
                if row_match:
                    found_rows = int(row_match.group(1))
                    estimated_rows = max(estimated_rows, found_rows)

        except Exception as e:
            explain_raw = f"EXPLAIN unavailable in preview mode: {str(e)}"
            # Fallback heuristic calculation
            estimated_rows = len(tables_involved) * 25000 if not has_where_clause else 1250

        # 3. Guardrail Threshold Evaluation
        if estimated_rows > self.MAX_ESTIMATED_ROWS_THRESHOLD:
            is_cost_exceeded = True
            warnings.append(f"High scan volume estimated ({estimated_rows:,} rows). Consider adding partition or index filters.")

        if not has_where_clause and len(tables_involved) > 0:
            warnings.append("Full table scan detected: Query lacks WHERE predicates.")

        cost_rating = "OPTIMAL"
        if has_cartesian_product or is_cost_exceeded:
            cost_rating = "CRITICAL_OVERHEAD"
        elif len(warnings) > 0:
            cost_rating = "MODERATE_WARNING"

        return {
            "estimated_rows": estimated_rows,
            "cost_rating": cost_rating,
            "is_cost_exceeded": is_cost_exceeded,
            "has_cartesian_product": has_cartesian_product,
            "table_count": len(tables_involved),
            "join_count": join_count,
            "has_where_clause": has_where_clause,
            "warnings": warnings,
            "explain_plan_raw": explain_raw if explain_raw else "Physical Plan: Direct Scan -> Filter -> Aggregation -> Limit",
            "plan_nodes": plan_nodes[:6],
        }


cost_estimator = QueryPerformanceCostEstimator()
