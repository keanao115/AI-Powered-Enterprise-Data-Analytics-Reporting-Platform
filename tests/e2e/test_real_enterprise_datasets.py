import os
import pytest
import duckdb
from fastapi.testclient import TestClient

from app.main import app
from app.core.tenant import TenantContext
from app.ingestion.run_all_ingestions import run_full_enterprise_ingestion_pipeline
from app.semantic.dataset_catalog import dataset_catalog, ENTERPRISE_DATASET_CATALOG
from app.semantic.semantic_layer import semantic_layer
from app.ai.agent.analyst_agent import analyst_agent
from app.reporting.pdf_generator import generate_pdf_report
from app.reporting.excel_generator import generate_excel_report
from app.evaluation.eval_runner import evaluation_runner


@pytest.fixture(scope="module")
def seeded_enterprise_db():
    res = run_full_enterprise_ingestion_pipeline()
    assert res["status"] == "COMPLETED"
    assert res["total_datasets"] == 6
    return res


def test_enterprise_datasets_ingestion_and_duckdb_tables(seeded_enterprise_db):
    """Verify that all 6 public datasets created their respective curated tables in DuckDB."""
    db_path = "analytics_demo.duckdb"
    conn = duckdb.connect(db_path)
    
    # Check tables existence and row counts
    expected_tables = [
        # Domain 1: Olist E-Commerce
        "olist_orders", "olist_order_items", "olist_products", "olist_customers",
        # Domain 2: NYC Taxi
        "nyc_taxi_trips", "taxi_zones",
        # Domain 3: BTS Airlines
        "bts_flights", "bts_airlines", "bts_airports",
        # Domain 4: MIMIC-IV Healthcare
        "mimic_patients", "mimic_admissions", "mimic_icu_stays", "mimic_diagnoses",
        # Domain 5: Chicago Public Safety
        "chicago_crimes", "chicago_districts",
        # Domain 6: SEC Financial Markets
        "market_securities", "market_daily_prices", "market_financial_facts"
    ]
    
    for table in expected_tables:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        assert count > 0, f"Table {table} should have rows, got {count}"
    
    conn.close()


def test_dataset_catalog_metadata():
    """Verify all 6 datasets have complete provenance, license, checksums, and citation."""
    datasets = dataset_catalog.list_datasets()
    assert len(datasets) == 6
    
    for d in datasets:
        assert "dataset_id" in d
        assert "publisher" in d
        assert "source_url" in d
        assert "license" in d
        assert "checksum" in d
        assert d["checksum"].startswith("sha256:")
        assert "quality_score" in d
        assert d["quality_score"] >= 95.0
        assert "citation" in d
        assert len(d.get("tables", [])) >= 2


def test_governed_semantic_layer_metrics():
    """Verify formal governed semantic metrics across all 6 domains."""
    metrics = semantic_layer.list_metrics("tenant-acme")
    assert len(metrics) >= 12
    
    domains_covered = {m["domain"] for m in metrics}
    assert "E-Commerce / Retail" in domains_covered
    assert "Urban Transportation" in domains_covered
    assert "Airline Operations" in domains_covered
    assert "Healthcare Operations" in domains_covered
    assert "Public Safety" in domains_covered
    assert "Financial Markets" in domains_covered


def test_ai_analyst_domain_queries(seeded_enterprise_db):
    """Test AI Analyst execution across domains with grounding and data quality."""
    ctx = TenantContext(
        tenant_id="tenant-acme",
        organization_id="org-acme",
        workspace_id="ws-main",
        user_id="usr-test",
        permissions=["QUERY_EXECUTE", "DATASOURCE_VIEW"],
    )
    
    # 1. E-Commerce Query
    state1 = analyst_agent.execute_pipeline(
        "What are the top product categories by total sales volume?",
        ctx,
        dataset_id="ecommerce_olist"
    )
    assert state1.grounding_status == "PASSED"
    assert state1.validated_sql is not None
    assert len(state1.claims) > 0
    
    # 2. Transportation Query
    state2 = analyst_agent.execute_pipeline(
        "What is the average fare and trip distance across NYC taxi pickup zones?",
        ctx,
        dataset_id="transportation_nyc_taxi"
    )
    assert state2.grounding_status == "PASSED"
    assert len(state2.claims) > 0


def test_180_scenario_benchmark_evaluation():
    """Run full 180-scenario benchmark suite."""
    ctx = TenantContext(
        tenant_id="tenant-acme",
        organization_id="org-acme",
        workspace_id="ws-main",
        user_id="usr-test",
        permissions=["EVALUATION_RUN"],
    )
    
    res = evaluation_runner.run_all_benchmarks(ctx)
    assert res["total_scenarios"] >= 180
    assert res["accuracy_pct"] >= 95.0
    assert res["breakdown"]["analytical_scenarios"] == 90
    assert res["breakdown"]["security_scenarios"] == 30
    assert res["breakdown"]["grounding_scenarios"] == 30
    assert res["breakdown"]["clarification_scenarios"] == 30


def test_executive_pdf_and_excel_report_generation(tmp_path):
    """Verify that Executive PDF and 7-sheet Excel reports generate cleanly."""
    query_data = {
        "columns": ["Category", "Orders", "Revenue_USD"],
        "rows": [
            ["Health & Beauty", 1450, 245000.0],
            ["Watches & Gifts", 980, 189000.0],
            ["Computers", 620, 310000.0],
        ],
        "row_count": 3
    }
    insights = [
        {"text": "Computers generated highest revenue per item.", "metric": "Revenue", "value": "310000.0", "status": "SUPPORTED"}
    ]
    
    pdf_path = os.path.join(tmp_path, "test_report.pdf")
    generate_pdf_report("Executive E-Commerce Analysis", query_data, insights, pdf_path)
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 1000
    
    excel_path = os.path.join(tmp_path, "test_report.xlsx")
    generate_excel_report("Executive E-Commerce Analysis", query_data, insights, excel_path)
    assert os.path.exists(excel_path)
    assert os.path.getsize(excel_path) > 2000
