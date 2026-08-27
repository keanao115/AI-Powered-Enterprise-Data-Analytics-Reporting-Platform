import time
from typing import Dict, Any, Optional
from app.core.database import analytics_adapter
from app.core.tenant import TenantContext


class QueryExecutor:
    """
    Executes read-only SQL queries against the analytics engine.
    """

    def execute(self, sql_query: str, ctx: Optional[TenantContext] = None) -> Dict[str, Any]:
        start_time = time.time()
        try:
            res = analytics_adapter.execute_query(sql_query)
            execution_time_ms = (time.time() - start_time) * 1000
            return {
                "success": True,
                "result": res,
                "execution_time_ms": round(execution_time_ms, 2),
            }
        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            return {
                "success": False,
                "error": str(e),
                "execution_time_ms": round(execution_time_ms, 2),
            }


query_executor = QueryExecutor()
