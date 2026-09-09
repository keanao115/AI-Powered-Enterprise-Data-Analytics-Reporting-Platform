import abc
import hashlib
import time
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple
from app.core.config import settings


class TokenBudgetExceededException(Exception):
    """Raised when tenant exceeds assigned token or cost allowance."""
    pass


class RateLimitExceededException(Exception):
    """Raised when tenant/user exceeds requests per minute threshold."""
    pass


class TokenGovernanceStorageBackend(abc.ABC):
    """
    Abstract interface for Token Governance state persistence.
    Allows seamlessly switching between in-memory tracking and distributed Redis.
    Remediates Item 3.3.
    """

    @abc.abstractmethod
    def record_request(self, tenant_id: str, timestamp: float, window_seconds: float) -> int:
        pass

    @abc.abstractmethod
    def add_request(self, tenant_id: str, timestamp: float) -> None:
        pass

    @abc.abstractmethod
    def check_and_deduct_tokens(
        self,
        tenant_id: str,
        estimated_tokens: int,
        estimated_cost_usd: float,
        daily_limit: int,
    ) -> Tuple[bool, Dict[str, float]]:
        pass

    @abc.abstractmethod
    def record_query_replay(
        self,
        tenant_id: str,
        query_hash: str,
        timestamp: float,
        window_seconds: float,
    ) -> int:
        pass

    @abc.abstractmethod
    def get_stats(self, tenant_id: str, daily_limit: int, rpm_limit: int) -> Dict[str, float]:
        pass


class InMemoryTokenGovernanceStorage(TokenGovernanceStorageBackend):
    """
    High-performance in-memory sliding window implementation.
    Standard default for single-node deployments and developer environments.
    """

    def __init__(self):
        self._tenant_usage: Dict[str, Dict[str, float]] = defaultdict(
            lambda: {"tokens": 0, "cost_usd": 0.0, "last_reset": time.time()}
        )
        self._request_timestamps: Dict[str, List[float]] = defaultdict(list)
        self._query_replay_history: Dict[str, Dict[str, List[float]]] = defaultdict(
            lambda: defaultdict(list)
        )

    def _maybe_reset_daily(self, tenant_id: str):
        now = time.time()
        record = self._tenant_usage[tenant_id]
        if now - record["last_reset"] >= 86400:
            record["tokens"] = 0
            record["cost_usd"] = 0.0
            record["last_reset"] = now

    def record_request(self, tenant_id: str, timestamp: float, window_seconds: float) -> int:
        window_start = timestamp - window_seconds
        timestamps = self._request_timestamps[tenant_id]
        self._request_timestamps[tenant_id] = [t for t in timestamps if t > window_start]
        return len(self._request_timestamps[tenant_id])

    def add_request(self, tenant_id: str, timestamp: float) -> None:
        self._request_timestamps[tenant_id].append(timestamp)

    def check_and_deduct_tokens(
        self,
        tenant_id: str,
        estimated_tokens: int,
        estimated_cost_usd: float,
        daily_limit: int,
    ) -> Tuple[bool, Dict[str, float]]:
        self._maybe_reset_daily(tenant_id)
        record = self._tenant_usage[tenant_id]

        if (record["tokens"] + estimated_tokens) > daily_limit:
            return False, {
                "used_tokens": record["tokens"],
                "limit_tokens": daily_limit,
                "requested_tokens": estimated_tokens,
                "used_cost_usd": record["cost_usd"],
            }

        record["tokens"] += estimated_tokens
        record["cost_usd"] += estimated_cost_usd

        return True, {
            "used_tokens": record["tokens"],
            "limit_tokens": daily_limit,
            "used_cost_usd": record["cost_usd"],
        }

    def record_query_replay(
        self,
        tenant_id: str,
        query_hash: str,
        timestamp: float,
        window_seconds: float,
    ) -> int:
        timestamps = self._query_replay_history[tenant_id][query_hash]
        valid_ts = [t for t in timestamps if timestamp - t <= window_seconds]
        valid_ts.append(timestamp)
        self._query_replay_history[tenant_id][query_hash] = valid_ts
        return len(valid_ts)

    def get_stats(self, tenant_id: str, daily_limit: int, rpm_limit: int) -> Dict[str, float]:
        self._maybe_reset_daily(tenant_id)
        record = self._tenant_usage[tenant_id]
        return {
            "daily_tokens_used": record["tokens"],
            "daily_token_limit": daily_limit,
            "daily_cost_usd": round(record["cost_usd"], 6),
            "current_rpm": len(self._request_timestamps[tenant_id]),
            "rpm_limit": rpm_limit,
        }


class RedisTokenGovernanceStorage(TokenGovernanceStorageBackend):
    """
    Distributed Redis-backed storage adapter for multi-instance production deployments.
    Uses Redis sorted sets (ZADD, ZREMRANGEBYSCORE, ZCARD) and atomic counters (INCRBY).
    Remediates Item 3.3 (Token governance multi-instance scalability).
    """

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_url = redis_url
        self._fallback = InMemoryTokenGovernanceStorage()
        self._redis_client = None

    def _get_client(self):
        if self._redis_client is None:
            try:
                import redis
                self._redis_client = redis.from_url(self.redis_url)
            except Exception:
                self._redis_client = None
        return self._redis_client

    def record_request(self, tenant_id: str, timestamp: float, window_seconds: float) -> int:
        client = self._get_client()
        if not client:
            return self._fallback.record_request(tenant_id, timestamp, window_seconds)
        try:
            key = f"ratelimit:{tenant_id}"
            window_start = timestamp - window_seconds
            pipe = client.pipeline()
            pipe.zremrangebyscore(key, "-inf", window_start)
            pipe.zcard(key)
            _, current_count = pipe.execute()
            return current_count
        except Exception:
            return self._fallback.record_request(tenant_id, timestamp, window_seconds)

    def add_request(self, tenant_id: str, timestamp: float) -> None:
        client = self._get_client()
        if not client:
            return self._fallback.add_request(tenant_id, timestamp)
        try:
            key = f"ratelimit:{tenant_id}"
            pipe = client.pipeline()
            pipe.zadd(key, {str(timestamp): timestamp})
            pipe.expire(key, 120)
            pipe.execute()
        except Exception:
            self._fallback.add_request(tenant_id, timestamp)

    def check_and_deduct_tokens(
        self,
        tenant_id: str,
        estimated_tokens: int,
        estimated_cost_usd: float,
        daily_limit: int,
    ) -> Tuple[bool, Dict[str, float]]:
        client = self._get_client()
        if not client:
            return self._fallback.check_and_deduct_tokens(tenant_id, estimated_tokens, estimated_cost_usd, daily_limit)
        try:
            date_str = time.strftime("%Y%m%d")
            key = f"tokenbudget:{tenant_id}:{date_str}"
            current = int(client.get(key) or 0)
            if current + estimated_tokens > daily_limit:
                return False, {
                    "used_tokens": current,
                    "limit_tokens": daily_limit,
                    "requested_tokens": estimated_tokens,
                    "used_cost_usd": 0.0,
                }
            pipe = client.pipeline()
            pipe.incrby(key, estimated_tokens)
            pipe.expire(key, 86400 * 2)
            pipe.execute()
            return True, {
                "used_tokens": current + estimated_tokens,
                "limit_tokens": daily_limit,
                "used_cost_usd": estimated_cost_usd,
            }
        except Exception:
            return self._fallback.check_and_deduct_tokens(tenant_id, estimated_tokens, estimated_cost_usd, daily_limit)

    def record_query_replay(
        self,
        tenant_id: str,
        query_hash: str,
        timestamp: float,
        window_seconds: float,
    ) -> int:
        client = self._get_client()
        if not client:
            return self._fallback.record_query_replay(tenant_id, query_hash, timestamp, window_seconds)
        try:
            key = f"replay:{tenant_id}:{query_hash}"
            window_start = timestamp - window_seconds
            pipe = client.pipeline()
            pipe.zremrangebyscore(key, "-inf", window_start)
            pipe.zadd(key, {str(timestamp): timestamp})
            pipe.zcard(key)
            pipe.expire(key, int(window_seconds * 2))
            _, _, count, _ = pipe.execute()
            return count
        except Exception:
            return self._fallback.record_query_replay(tenant_id, query_hash, timestamp, window_seconds)

    def get_stats(self, tenant_id: str, daily_limit: int, rpm_limit: int) -> Dict[str, float]:
        client = self._get_client()
        if not client:
            return self._fallback.get_stats(tenant_id, daily_limit, rpm_limit)
        try:
            date_str = time.strftime("%Y%m%d")
            used_tokens = int(client.get(f"tokenbudget:{tenant_id}:{date_str}") or 0)
            current_rpm = client.zcard(f"ratelimit:{tenant_id}")
            return {
                "daily_tokens_used": used_tokens,
                "daily_token_limit": daily_limit,
                "daily_cost_usd": 0.0,
                "current_rpm": current_rpm,
                "rpm_limit": rpm_limit,
            }
        except Exception:
            return self._fallback.get_stats(tenant_id, daily_limit, rpm_limit)


class TokenGovernanceManager:
    """
    Multi-tenant LLM Cost & Abuse Governance.
    Provides:
    1. Per-tenant daily token and cost budgeting.
    2. Sliding-window rate limiting (Requests Per Minute).
    3. High-frequency repetitive query detection (Replay/Spam protection).
    Supports pluggable storage backends (InMemory for single-node / Redis for distributed clusters).
    """

    def __init__(
        self,
        daily_token_limit: Optional[int] = None,
        rpm_limit: Optional[int] = None,
        storage_backend: Optional[TokenGovernanceStorageBackend] = None,
    ):
        self.daily_token_limit = daily_token_limit or settings.PER_TENANT_DAILY_TOKEN_BUDGET
        self.rpm_limit = rpm_limit or settings.PER_TENANT_RATE_LIMIT_RPM
        self.storage: TokenGovernanceStorageBackend = storage_backend or InMemoryTokenGovernanceStorage()

    def check_rate_limit(self, tenant_id: str, max_rpm: Optional[int] = None) -> Tuple[bool, int]:
        """
        Sliding-window check for Requests Per Minute (RPM).
        Returns (allowed, current_count).
        """
        now = time.time()
        limit = max_rpm or self.rpm_limit
        current_count = self.storage.record_request(tenant_id, now, window_seconds=60.0)

        if current_count >= limit:
            return False, current_count

        self.storage.add_request(tenant_id, now)
        return True, current_count + 1

    def check_and_deduct_tokens(
        self,
        tenant_id: str,
        estimated_tokens: int,
        estimated_cost_usd: float = 0.0,
    ) -> Tuple[bool, Dict[str, float]]:
        """
        Checks if tenant has remaining daily token allowance.
        """
        return self.storage.check_and_deduct_tokens(
            tenant_id=tenant_id,
            estimated_tokens=estimated_tokens,
            estimated_cost_usd=estimated_cost_usd,
            daily_limit=self.daily_token_limit,
        )

    def detect_query_anomaly(
        self,
        tenant_id: str,
        query_text: str,
        window_seconds: int = 30,
        max_repeats: int = 5,
    ) -> bool:
        """
        Detects repetitive identical queries in short time windows (potential scraping or infinite retry loop).
        Returns True if anomalous repetition detected.
        """
        now = time.time()
        q_hash = hashlib.sha256(query_text.strip().lower().encode("utf-8")).hexdigest()
        count = self.storage.record_query_replay(tenant_id, q_hash, now, window_seconds)
        return count > max_repeats

    def get_tenant_stats(self, tenant_id: str) -> Dict[str, float]:
        return self.storage.get_stats(tenant_id, self.daily_token_limit, self.rpm_limit)


token_governance = TokenGovernanceManager()
