import pytest
import time
from app.ai.resilience import CircuitBreaker, retry_with_exponential_backoff
from app.analytics.grounding import GroundingValidator
from app.semantic.semantic_layer import semantic_layer


def test_circuit_breaker_transitions():
    cb = CircuitBreaker(name="TestBreaker", failure_threshold=2, recovery_timeout=0.2)
    assert cb.state == "CLOSED"
    assert cb.can_execute() is True

    # 1st failure
    cb.record_failure(Exception("Timeout 1"))
    assert cb.state == "CLOSED"
    assert cb.can_execute() is True

    # 2nd failure -> Should trip to OPEN
    cb.record_failure(Exception("Timeout 2"))
    assert cb.state == "OPEN"
    assert cb.can_execute() is False

    # Execution with fallback when OPEN
    executed_target = False
    executed_fallback = False

    def target():
        nonlocal executed_target
        executed_target = True
        return "target_result"

    def fallback():
        nonlocal executed_fallback
        executed_fallback = True
        return "fallback_result"

    res = cb.execute_with_fallback(target, fallback)
    assert res == "fallback_result"
    assert executed_target is False
    assert executed_fallback is True

    # Wait for recovery timeout -> should transition to HALF_OPEN
    time.sleep(0.25)
    assert cb.can_execute() is True
    assert cb.state == "HALF_OPEN"

    # Success in HALF_OPEN resets to CLOSED
    cb.record_success()
    assert cb.state == "CLOSED"


def test_exponential_backoff_retry():
    calls = 0

    def flaky_function():
        nonlocal calls
        calls += 1
        if calls < 2:
            raise ConnectionError("Transient network failure")
        return "recovered"

    result = retry_with_exponential_backoff(
        flaky_function,
        max_retries=2,
        base_delay=0.05,
        max_delay=0.2,
        jitter=False
    )
    assert result == "recovered"
    assert calls == 2


def test_empirical_fact_grounding_numerical_verification():
    validator = GroundingValidator(tolerance_pct=0.5)

    # Simulated query result data
    query_data = {
        "columns": ["category", "total_orders", "revenue_usd", "late_rate_pct"],
        "rows": [
            ["Health & Beauty", 1450, 245000.0, 4.25],
            ["Electronics", 890, 185200.5, 6.10],
        ]
    }

    # 1. Exact & tolerance matched claim
    claims_supported = [
        {"claim_id": "c1", "text": "Health & Beauty delivered 1450 orders totaling $245,000 in revenue."},
        {"claim_id": "c2", "text": "Electronics experienced a 6.1% late delivery rate across 890 orders."},
    ]
    res1 = validator.validate_claims(claims_supported, query_data)
    assert len(res1) == 2
    assert res1[0]["status"] == "SUPPORTED"
    assert res1[1]["status"] == "SUPPORTED"

    # 2. Unsupported / hallucinated claim
    claims_unsupported = [
        {"claim_id": "c3", "text": "Health & Beauty orders reached 999999 with revenue of $99,999,999."},
    ]
    res2 = validator.validate_claims(claims_unsupported, query_data)
    assert res2[0]["status"] == "UNSUPPORTED"

    # 3. KPI summary computation
    kpi = validator.compute_summary_kpi(res1 + res2)
    assert kpi["total_claims"] == 3
    assert kpi["supported"] == 2
    assert kpi["unsupported"] == 1
    assert kpi["grounding_rate_pct"] == 66.67


def test_semantic_layer_metric_versioning_and_audit():
    # Retrieve existing metric
    metric = semantic_layer.get_metric("gross_merchandise_value")
    assert metric is not None
    assert metric.version == "1.0.0"

    # Mutate formula with governed audit history
    updated = semantic_layer.update_metric_formula(
        metric_key="gross_merchandise_value",
        new_formula="SUM(price + freight_value) - SUM(discount_value)",
        user_id="lead_analyst_jane",
        reason="Account for promotional discounts in adjusted GMV",
        new_version="1.1.0",
    )
    assert updated.version == "1.1.0"
    assert "discount_value" in updated.formula

    # Check history
    history = semantic_layer.get_metric_history("gross_merchandise_value")
    assert len(history) >= 1
    assert history[-1]["version"] == "1.0.0"
    assert history[-1]["author"] == "lead_analyst_jane"
    assert "promotional discounts" in history[-1]["reason"]
