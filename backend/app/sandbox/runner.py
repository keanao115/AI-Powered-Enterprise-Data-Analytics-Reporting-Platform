import sys
import io
import traceback
from typing import Any, Dict
from app.sandbox.code_validator import code_validator


class SandboxRunner:
    """
    Isolated Sandbox Process Runner executing Python data code.
    Enforces AST static safety checks and executes code in a restricted scope.
    """

    def run_code(self, python_code: str, data: Dict[str, Any]) -> Dict[str, Any]:
        # 1. AST Validation
        is_safe, reason = code_validator.validate(python_code)
        if not is_safe:
            return {"success": False, "error": f"Sandbox Security Check Blocked Code: {reason}"}

        # 2. Prepare Isolated Scope
        local_scope = {"data": data, "result": None}
        
        # Capture stdout
        old_stdout = sys.stdout
        redirected_output = sys.stdout = io.StringIO()

        try:
            exec(python_code, {"__builtins__": __builtins__}, local_scope)
            sys.stdout = old_stdout
            res = local_scope.get("result") or {"output": redirected_output.getvalue()}
            return {"success": True, "result": res}
        except Exception as e:
            sys.stdout = old_stdout
            return {"success": False, "error": f"Execution Error: {str(e)}", "traceback": traceback.format_exc()}


sandbox_runner = SandboxRunner()
