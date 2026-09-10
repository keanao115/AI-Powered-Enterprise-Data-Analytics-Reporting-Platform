import time
from typing import Dict, Any, Optional
from app.core.tenant import TenantContext
from app.core.database import analytics_adapter


class QueryExecutor:
    """
    QueryExecutor proxy delegating to the unified SecureQueryGateway when context is present,
    or executing directly against analytics_adapter for internal raw queries.
    """

    def execute(self, sql_query: str, ctx: Optional[TenantContext] = None) -> Dict[str, Any]:
        if ctx is not None:
            from app.query_engine.secure_gateway import secure_query_gateway
            return secure_query_gateway.execute(sql_query, ctx=ctx, purpose="query_executor")

        # Raw internal execution when no tenant context is bound (e.g. initial setup / admin test)
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
