from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class PlatformException(HTTPException):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(
            status_code=status_code,
            detail={"code": code, "message": message, "details": self.details},
        )


class AuthenticationException(PlatformException):
    def __init__(self, message: str = "Invalid credentials or token expired"):
        super().__init__(
            code="AUTHENTICATION_FAILED",
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class AuthorizationDeniedException(PlatformException):
    def __init__(self, message: str = "Permission denied for this operation"):
        super().__init__(
            code="AUTHORIZATION_DENIED",
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class TenantAccessDeniedException(PlatformException):
    def __init__(self, message: str = "Access to requested tenant resource denied"):
        super().__init__(
            code="TENANT_ACCESS_DENIED",
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class SQLPolicyDeniedException(PlatformException):
    def __init__(self, reason: str, query: Optional[str] = None):
        super().__init__(
            code="QUERY_POLICY_DENIED",
            message=f"SQL query blocked by security policy: {reason}",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"reason": reason, "query": query},
        )


class PromptInjectionException(PlatformException):
    def __init__(self, reason: str):
        super().__init__(
            code="PROMPT_INJECTION_BLOCKED",
            message=f"Prompt security screening blocked request: {reason}",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"reason": reason},
        )


class PIIAccessDeniedException(PlatformException):
    def __init__(self, field_name: str):
        super().__init__(
            code="PII_ACCESS_DENIED",
            message=f"Access to sensitive field '{field_name}' denied by data governance policy",
            status_code=status.HTTP_403_FORBIDDEN,
            details={"field": field_name},
        )


class ClarificationRequiredException(PlatformException):
    def __init__(self, ambiguity_type: str, options: list):
        super().__init__(
            code="CLARIFICATION_REQUIRED",
            message="Query intent is ambiguous; user clarification required",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"ambiguity_type": ambiguity_type, "options": options},
        )


class GroundingValidationException(PlatformException):
    def __init__(self, unsupported_claims: list):
        super().__init__(
            code="GROUNDING_FAILED",
            message="AI insight contains claims not supported by query results",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"unsupported_claims": unsupported_claims},
        )


class SandboxExecutionException(PlatformException):
    def __init__(self, reason: str):
        super().__init__(
            code="SANDBOX_EXECUTION_FAILED",
            message=f"Sandboxed Python execution failed: {reason}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"reason": reason},
        )
