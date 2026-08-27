import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from app.core.tenant import TenantContext

logger = logging.getLogger("audit")


class AuditLogger:
    """
    Immutable Audit Event Logger recording security-sensitive operations.
    """

    def log_event(
        self,
        action: str,
        resource: str,
        result: str,
        risk_level: str = "LOW",
        reason: Optional[str] = None,
        ctx: Optional[TenantContext] = None,
        request_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        event_id = f"aud-{uuid.uuid4().hex[:12]}"
        audit_entry = {
            "event_id": event_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tenant_id": ctx.tenant_id if ctx else "SYSTEM",
            "user_id": ctx.user_id if ctx else "SYSTEM",
            "request_id": request_id or "N/A",
            "action": action,
            "resource": resource,
            "result": result,
            "risk_level": risk_level,
            "reason": reason or "",
            "details": details or {},
        }
        logger.info(f"AUDIT_EVENT: {audit_entry}")
        return audit_entry


audit_logger = AuditLogger()
