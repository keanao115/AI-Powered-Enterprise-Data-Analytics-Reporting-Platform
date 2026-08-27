from typing import Dict, Any, Optional
from app.core.tenant import TenantContext
from app.ai.llm_gateway import llm_gateway
from app.ai.schemas.llm_schemas import LLMMessage
from app.ai.prompts.prompts import SQL_REPAIR_PROMPT
from app.query_engine.ast_policy import ast_policy_engine
from app.query_engine.executor import query_executor


class SQLRepairService:
    MAX_ATTEMPTS = 3

    def repair_and_execute(
        self, failed_sql: str, error_message: str, ctx: TenantContext
    ) -> Dict[str, Any]:
        current_sql = failed_sql
        current_error = error_message

        for attempt in range(1, self.MAX_ATTEMPTS + 1):
            prompt = SQL_REPAIR_PROMPT.format(
                original_sql=current_sql,
                error_message=current_error,
                schema_catalog="orders, products, returns, regions",
            )
            llm_resp = llm_gateway.generate([
                LLMMessage(role="system", content="Fix the SQL query error."),
                LLMMessage(role="user", content=prompt)
            ])

            # Extract repaired SQL
            repaired_sql = llm_resp.content.strip()
            if "```sql" in repaired_sql:
                repaired_sql = repaired_sql.split("```sql")[1].split("```")[0].strip()

            # Validate AST policy again
            policy_check = ast_policy_engine.validate(repaired_sql, ctx)
            if not policy_check["allowed"]:
                current_error = f"Policy violation on repair attempt {attempt}: {policy_check['reason']}"
                continue

            # Execute
            exec_res = query_executor.execute(repaired_sql, ctx)
            if exec_res["success"]:
                exec_res["repaired"] = True
                exec_res["attempts"] = attempt
                return exec_res

            current_sql = repaired_sql
            current_error = exec_res["error"]

        return {
            "success": False,
            "error": f"SQL Repair failed after {self.MAX_ATTEMPTS} attempts. Last error: {current_error}",
            "attempts": self.MAX_ATTEMPTS,
        }


sql_repair_service = SQLRepairService()
