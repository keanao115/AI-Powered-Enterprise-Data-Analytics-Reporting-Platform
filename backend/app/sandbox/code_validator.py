import ast
from typing import Tuple, Set


class PythonCodeASTValidator:
    """
    Static Python AST Inspector enforcing sandbox isolation policies.
    Blocks dangerous modules, subprocesses, network sockets, file I/O, and reflection.
    """

    PROHIBITED_MODULES: Set[str] = {
        "os",
        "sys",
        "subprocess",
        "socket",
        "pathlib",
        "shutil",
        "ctypes",
        "multiprocessing",
        "threading",
        "importlib",
        "asyncio",
        "requests",
        "urllib",
        "httpx",
    }

    PROHIBITED_FUNCTIONS: Set[str] = {
        "eval",
        "exec",
        "compile",
        "open",
        "__import__",
        "getattr",
        "setattr",
        "delattr",
    }

    def validate(self, python_code: str) -> Tuple[bool, str]:
        try:
            tree = ast.parse(python_code)
        except SyntaxError as e:
            return False, f"Python Syntax Error: {str(e)}"

        for node in ast.walk(tree):
            # Check import statements
            if isinstance(node, ast.Import):
                for alias in node.names:
                    mod = alias.name.split(".")[0]
                    if mod in self.PROHIBITED_MODULES:
                        return False, f"Prohibited module import: '{mod}'"

            elif isinstance(node, ast.ImportFrom):
                mod = (node.module or "").split(".")[0]
                if mod in self.PROHIBITED_MODULES:
                    return False, f"Prohibited module import from: '{mod}'"

            # Check function calls
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.PROHIBITED_FUNCTIONS:
                        return False, f"Prohibited function call: '{node.func.id}()'"

        return True, "AST_VALIDATION_PASSED"


code_validator = PythonCodeASTValidator()
