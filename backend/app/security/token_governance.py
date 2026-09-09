import time
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from app.core.config import settings


class TokenBudgetExceededException(Exception):
    """Raised when tenant exceeds assigned token or cost allowance."""
    pass


class RateLimitExceededException(Exception):
    """Raised when tenant/user exceeds requests per minute threshold."""
    pass


class TokenGovernanceManager:
    """
    Multi-tenant LLM Cost & Abuse Governance.
    Provides:
    1. Per-tenant daily token and cost budgeting.
    2. Sliding-window rate limiting (Requests Per Minute).
    3. High-frequency repetitive query detection (Replay/Spam protection).
    """

    def __init__(
        self,
        daily_token_limit: Optional[int] = None,
        rpm_limit: Optional[int] = None,
    ):
        self.daily_token_limit = daily_token_limit or settings.PER_TENANT_DAILY_TOKEN_BUDGET
        self.rpm_limit = rpm_limit or settings.PER_TENANT_RATE_LIMIT_RPM

        # In-memory tracking structures (in production, backed by Redis)
        # {tenant_id: {"tokens": int, "cost_usd": float, "last_reset": float}}
        self._tenant_usage: Dict[str, Dict[str, float]] = defaultdict(
            lambda: {"tokens": 0, "cost_usd": 0.0, "last_reset": time.time()}
        )

        # {tenant_id: [timestamp, timestamp, ...]}
        self._request_timestamps: Dict[str, List[float]] = defaultdict(list)

        # {tenant_id: {query_hash: [timestamp, timestamp, ...]}}
        self._query_replay_history: Dict[str, Dict[str, List[float]]] = defaultdict(
            lambda: defaultdict(list)
        )

    def _maybe_reset_daily(self, tenant_id: str):
        now = time.time()
        record = self._tenant_usage[tenant_id]
        # 86400 seconds = 24 hours
        if now - record["last_reset"] >= 86400:
            record["tokens"] = 0
            record["cost_usd"] = 0.0
            record["last_reset"] = now

    def check_rate_limit(self, tenant_id: str, max_rpm: Optional[int] = None) -> Tuple[bool, int]:
        """
        Sliding-window check for Requests Per Minute (RPM).
        Returns (allowed, current_count).
        """
        now = time.time()
        limit = max_rpm or self.rpm_limit
        window_start = now - 60.0

        timestamps = self._request_timestamps[tenant_id]
        # Evict timestamps outside 60s window
        self._request_timestamps[tenant_id] = [t for t in timestamps if t > window_start]
        current_count = len(self._request_timestamps[tenant_id])

        if current_count >= limit:
            return False, current_count

        self._request_timestamps[tenant_id].append(now)
        return True, current_count + 1

    def check_and_deduct_tokens(
        self,
        tenant_id: str,
        estimated_tokens: int,
        estimated_cost_usd: float = 0.0
    ) -> Tuple[bool, Dict[str, float]]:
        """
        Checks if tenant has remaining daily token allowance.
        """
        self._maybe_reset_daily(tenant_id)
        record = self._tenant_usage[tenant_id]

        if (record["tokens"] + estimated_tokens) > self.daily_token_limit:
            return False, {
                "used_tokens": record["tokens"],
                "limit_tokens": self.daily_token_limit,
                "requested_tokens": estimated_tokens,
                "used_cost_usd": record["cost_usd"],
            }

        record["tokens"] += estimated_tokens
        record["cost_usd"] += estimated_cost_usd

        return True, {
            "used_tokens": record["tokens"],
            "limit_tokens": self.daily_token_limit,
            "used_cost_usd": record["cost_usd"],
        }

    def detect_query_anomaly(self, tenant_id: str, query_text: str, window_seconds: int = 30, max_repeats: int = 5) -> bool:
        """
        Detects repetitive identical queries in short time windows (potential scraping or infinite retry loop).
        Returns True if anomalous repetition detected.
        """
        import hashlib
        now = time.time()
        q_hash = hashlib.sha256(query_text.strip().lower().encode("utf-8")).hexdigest()

        timestamps = self._query_replay_history[tenant_id][q_hash]
        # Filter window
        valid_ts = [t for t in timestamps if now - t <= window_seconds]
        valid_ts.append(now)
        self._query_replay_history[tenant_id][q_hash] = valid_ts

        return len(valid_ts) > max_repeats

    def get_tenant_stats(self, tenant_id: str) -> Dict[str, float]:
        self._maybe_reset_daily(tenant_id)
        record = self._tenant_usage[tenant_id]
        return {
            "daily_tokens_used": record["tokens"],
            "daily_token_limit": self.daily_token_limit,
            "daily_cost_usd": round(record["cost_usd"], 6),
            "current_rpm": len(self._request_timestamps[tenant_id]),
            "rpm_limit": self.rpm_limit,
        }


token_governance = TokenGovernanceManager()
