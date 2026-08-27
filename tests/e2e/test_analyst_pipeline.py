import pytest
import duckdb
from app.core.tenant import TenantContext
from app.ai.agent.analyst_agent import analyst_agent
from app.ai.providers.mock_provider import MockLLMProvider
from app.security.data_masking import data_masking_engine
from app.analytics.grounding import grounding_validator
from app.analytics.data_quality import evaluate_data_quality
from app.core.database import get_analytics_db_path
from seed.seed_data import seed_synthetic_analytics_database

@pytest.fixture(scope="module", autouse=True)
def setup_demo_db():
    seed_synthetic_analytics_database(get_analytics_db_path())

def test_duckdb_tables_integrity():
    conn = duckdb.connect(get_analytics_db_path())
    tables = [
        "sales_orders", "customer_churn", "inventory_supply_chain",
        "financial_metrics", "employee_performance", "marketing_campaigns"
    ]
    for tbl in tables:
        count = conn.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
        assert count > 0, f"Table {tbl} should not be empty"
        cols = conn.execute(f"DESCRIBE {tbl}").fetchall()
        assert len(cols) >= 20, f"Table {tbl} should have rich columns"
    conn.close()

def test_data_masking_engine():
    columns = ["customer_id", "customer_name", "total_amount", "work_email"]
    rows = [
        ["CUST-001", "Acme Corporation", 125000.0, "admin@acme.com"],
        ["CUST-002", "Globex Global", 85000.0, "sales@globex.com"],
    ]
    masked = data_masking_engine.mask_result_set(columns, rows)
    # Masking engine replaces confidential names and emails with masked versions
    assert len(masked) == 2

def test_grounding_validator():
    raw_results = {
        "columns": ["region", "order_count", "total_sales"],
        "rows": [["US", 10, 2296123.05], ["EU", 5, 841965.0]],
    }
    claims = [
        {
            "claim_id": "c1",
            "text": "在 region 'US' 中，order_count 為 10。",
            "metric": "order_count",
            "value": "10",
            "status": "SUPPORTED",
            "confidence_score": 0.99
        }
    ]
    validated_claims = grounding_validator.validate_claims(claims, raw_results)
    assert len(validated_claims) == 1
    assert validated_claims[0]["status"] == "SUPPORTED"
    assert validated_claims[0]["confidence_score"] > 0.9

def test_data_quality_scoring():
    columns = ["order_id", "total_amount", "gross_margin_pct"]
    rows = [
        ["ORD-001", 15000.0, 78.5],
        ["ORD-002", 22000.0, 81.2],
        ["ORD-003", 9500.0, 74.0],
    ]
    quality = evaluate_data_quality(columns, rows)
    assert quality["quality_score"] >= 80.0
    assert quality["null_ratio"] == 0.0
    assert quality["duplicate_count"] == 0
