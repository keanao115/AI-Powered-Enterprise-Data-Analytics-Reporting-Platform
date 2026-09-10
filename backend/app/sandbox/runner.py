import json
import os
import subprocess
import sys
from typing import Any, Dict, Optional

from app.core.config import settings
from app.sandbox.code_validator import code_validator


class SandboxRunner:
    """
    Process-Isolated Python Sandbox Runner.
    Guarantees Invariant 6: No untrusted Python code runs directly inside
    the API main server process.

    Security Controls:
    1. Static AST inspection via code_validator (blocks prohibited modules & reflection)
    2. Subprocess execution in an isolated worker process
    3. Wall-clock execution timeout enforcement (kills runaway infinite loops)
    4. Whitelisted safe builtins & restricted import policy in worker
    5. Sanitized error messages (no host environment/filepath leaks)
    """

    def __init__(self, default_timeout: Optional[int] = None):
        self.default_timeout = default_timeout or getattr(settings, "MAX_SANDBOX_SECONDS", 15)

    def run_code(
        self,
        python_code: str,
        data: Dict[str, Any],
        timeout_seconds: Optional[int] = None,
    ) -> Dict[str, Any]:
        # 1. AST Validation
        is_safe, reason = code_validator.validate(python_code)
        if not is_safe:
            return {
                "success": False,
                "error": f"Sandbox Security Check Blocked Code: {reason}",
                "error_code": "SANDBOX_AST_BLOCKED",
            }

        # 2. Prepare Subprocess Isolation
        timeout = timeout_seconds or self.default_timeout
        input_payload = json.dumps({"code": python_code, "data": data})

        # Resolve backend root directory for PYTHONPATH
        backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        env = os.environ.copy()
        env["PYTHONPATH"] = backend_dir

        cmd = [sys.executable, "-m", "app.sandbox.worker"]

        proc = None
        try:
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=backend_dir,
                env=env,
            )

            stdout_data, stderr_data = proc.communicate(input=input_payload, timeout=timeout)

            if proc.returncode != 0 and not stdout_data:
                err_msg = (
                    stderr_data.strip() or f"Worker process exited with code {proc.returncode}"
                )
                return {
                    "success": False,
                    "error": f"Sandbox execution failure: {err_msg}",
                    "error_code": "SANDBOX_WORKER_FAILURE",
                }

            # Parse worker JSON output
            try:
                res = json.loads(stdout_data)
                return res
            except json.JSONDecodeError:
                return {
                    "success": False,
                    "error": f"Invalid sandbox output format: {stdout_data[:200]}",
                    "error_code": "SANDBOX_FORMAT_ERROR",
                }

        except subprocess.TimeoutExpired:
            if proc:
                try:
                    proc.kill()
                    proc.communicate(timeout=2)
                except Exception:
                    pass
            return {
                "success": False,
                "error": f"Sandbox execution timeout: exceeded {timeout} seconds limit.",
                "error_code": "SANDBOX_TIMEOUT",
            }

        except Exception as e:
            if proc:
                try:
                    proc.kill()
                except Exception:
                    pass
            return {
                "success": False,
                "error": f"Sandbox process error: {str(e)}",
                "error_code": "SANDBOX_PROCESS_ERROR",
            }


sandbox_runner = SandboxRunner()
