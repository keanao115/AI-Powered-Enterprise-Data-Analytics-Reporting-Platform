from app.security.token_governance import TokenGovernanceManager


def test_sliding_window_rate_limiter():
    manager = TokenGovernanceManager(daily_token_limit=10000, rpm_limit=3)
    tenant = "tenant-test-rpm"

    # First 3 requests should pass
    for i in range(3):
        allowed, count = manager.check_rate_limit(tenant)
        assert allowed is True
        assert count == i + 1

    # 4th request within same minute should be rejected
    allowed, count = manager.check_rate_limit(tenant)
    assert allowed is False
    assert count == 3


def test_token_budget_quota_enforcement():
    manager = TokenGovernanceManager(daily_token_limit=1000, rpm_limit=60)
    tenant = "tenant-test-budget"

    # Request within quota
    allowed, stats = manager.check_and_deduct_tokens(
        tenant, estimated_tokens=600, estimated_cost_usd=0.005
    )
    assert allowed is True
    assert stats["used_tokens"] == 600

    # Second request that exceeds quota (600 + 500 = 1100 > 1000)
    allowed, stats = manager.check_and_deduct_tokens(
        tenant, estimated_tokens=500, estimated_cost_usd=0.004
    )
    assert allowed is False
    assert stats["used_tokens"] == 600
    assert stats["limit_tokens"] == 1000


def test_query_replay_anomaly_detection():
    manager = TokenGovernanceManager()
    tenant = "tenant-anomaly-test"
    query = "SELECT * FROM sales_orders WHERE region = 'US'"

    # Send repeated query 5 times
    for _ in range(5):
        is_anomaly = manager.detect_query_anomaly(tenant, query, window_seconds=10, max_repeats=5)
        assert is_anomaly is False

    # 6th repeat exceeds threshold
    is_anomaly = manager.detect_query_anomaly(tenant, query, window_seconds=10, max_repeats=5)
    assert is_anomaly is True


def test_storage_backend_pluggability_and_redis_adapter():
    from app.security.token_governance import (
        InMemoryTokenGovernanceStorage,
        RedisTokenGovernanceStorage,
    )

    # 1. Custom InMemory storage
    in_mem_storage = InMemoryTokenGovernanceStorage()
    mgr1 = TokenGovernanceManager(rpm_limit=5, storage_backend=in_mem_storage)
    allowed, count = mgr1.check_rate_limit("t-custom-mem")
    assert allowed is True
    assert count == 1

    # 2. Redis adapter initialization and graceful local fallback
    redis_storage = RedisTokenGovernanceStorage("redis://non-existent-host:6379/0")
    mgr2 = TokenGovernanceManager(rpm_limit=5, storage_backend=redis_storage)
    allowed2, count2 = mgr2.check_rate_limit("t-redis-test")
    assert allowed2 is True
    assert count2 == 1
