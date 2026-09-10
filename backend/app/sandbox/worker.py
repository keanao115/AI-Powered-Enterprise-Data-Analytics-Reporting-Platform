import io
import json
import sys

ALLOWED_MODULES = {
    "matplotlib",
    "matplotlib.pyplot",
    "pandas",
    "numpy",
    "io",
    "base64",
    "json",
    "math",
    "datetime",
    "collections",
    "itertools",
    "re",
}

SAFE_BUILTINS = {
    "abs": abs,
    "all": all,
    "any": any,
    "bool": bool,
    "bytes": bytes,
    "dict": dict,
    "enumerate": enumerate,
    "filter": filter,
    "float": float,
    "format": format,
    "frozenset": frozenset,
    "int": int,
    "isinstance": isinstance,
    "issubclass": issubclass,
    "iter": iter,
    "len": len,
    "list": list,
    "map": map,
    "max": max,
    "min": min,
    "next": next,
    "pow": pow,
    "print": print,
    "range": range,
    "reversed": reversed,
    "round": round,
    "set": set,
    "slice": slice,
    "sorted": sorted,
    "str": str,
    "sum": sum,
    "tuple": tuple,
    "zip": zip,
    "True": True,
    "False": False,
    "None": None,
}


def _restricted_import(name, globals=None, locals=None, fromlist=(), level=0):
    root_mod = name.split(".")[0]
    if root_mod not in ALLOWED_MODULES:
        raise ImportError(
            f"Prohibited import: module '{name}' is disallowed by sandbox isolation policy."
        )
    return __import__(name, globals, locals, fromlist, level)


SAFE_BUILTINS["__import__"] = _restricted_import


def sanitize_error(err_str: str) -> str:
    """Removes sensitive host paths and internal environment details from error strings."""
    lines = err_str.strip().split("\n")
    cleaned = []
    for line in lines:
        if 'File "' in line:
            # Strip local drive/path details
            cleaned.append('  File "<sandbox>", line in code')
        else:
            cleaned.append(line)
    return "\n".join(cleaned[-3:])  # Return only the concise error message


def run_worker():
    try:
        raw_input = sys.stdin.read()
        if not raw_input:
            sys.stdout.write(json.dumps({"success": False, "error": "No input provided"}))
            return

        payload = json.loads(raw_input)
        python_code = payload.get("code", "")
        data = payload.get("data", {})

        local_scope = {"data": data, "result": None}
        captured_stdout = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured_stdout

        try:
            exec(python_code, {"__builtins__": SAFE_BUILTINS}, local_scope)
            sys.stdout = old_stdout
            res = local_scope.get("result")
            if res is None:
                res = {"output": captured_stdout.getvalue()}

            output_payload = {"success": True, "result": res}
            sys.stdout.write(json.dumps(output_payload))
        except Exception as exec_err:
            sys.stdout = old_stdout
            sanitized = sanitize_error(str(exec_err))
            output_payload = {
                "success": False,
                "error": f"Execution Error: {sanitized}",
                "error_code": "SANDBOX_RUNTIME_ERROR",
            }
            sys.stdout.write(json.dumps(output_payload))
    except Exception as e:
        sys.stdout = sys.__stdout__
        sys.stdout.write(json.dumps({"success": False, "error": sanitize_error(str(e))}))


if __name__ == "__main__":
    run_worker()
