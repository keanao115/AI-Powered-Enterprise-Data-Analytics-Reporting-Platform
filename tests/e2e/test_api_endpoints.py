import pytest
from app.core.database import get_analytics_db_path
from app.main import app
from fastapi.testclient import TestClient
from seed.seed_data import seed_synthetic_analytics_database


@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    seed_synthetic_analytics_database(get_analytics_db_path())


@pytest.fixture
def client():
    return TestClient(app)


def test_health_and_readiness_endpoints(client):
    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "HEALTHY"

    res_ready = client.get("/ready")
    assert res_ready.status_code == 200
    assert res_ready.json()["status"] == "READY"

    res_live = client.get("/live")
    assert res_live.status_code == 200
    assert res_live.json()["status"] == "ALIVE"


def test_datasets_endpoints(client):
    # 1. List 6 real datasets
    res = client.get("/api/v1/datasets")
    assert res.status_code == 200
    datasets = res.json()
    assert len(datasets) == 6
    expected_ids = {
        "ecommerce_olist",
        "transportation_nyc_taxi",
        "airline_bts_ontime",
        "healthcare_mimic_iv",
        "safety_chicago_crimes",
        "financial_sec_markets",
    }
    assert {d["dataset_id"] for d in datasets} == expected_ids

    # 2. Get details for ecommerce_olist
    res_detail = client.get("/api/v1/datasets/ecommerce_olist")
    assert res_detail.status_code == 200
    detail = res_detail.json()
    assert detail["metadata"]["dataset_id"] == "ecommerce_olist"
    assert detail["total_rows"] > 0
    assert len(detail["columns"]) > 0
    assert len(detail["rows"]) > 0

    # 3. CSV download
    res_csv = client.get("/api/v1/datasets/ecommerce_olist/download")
    assert res_csv.status_code == 200
    assert "text/csv" in res_csv.headers.get("content-type", "")


def test_schemas_endpoints(client):
    res = client.get("/api/v1/schemas")
    assert res.status_code == 200
    tables = res.json()
    assert len(tables) >= 6

    # Test catalog endpoint
    res_cat = client.get("/api/v1/schemas/catalog")
    assert res_cat.status_code == 200
    catalog = res_cat.json()
    assert len(catalog) >= 6
    for item in catalog:
        assert "name" in item
        assert "desc" in item
        assert "columns" in item
        assert isinstance(item["columns"], list)


def test_audit_logs_endpoint(client):
    res = client.get("/api/v1/audit")
    assert res.status_code == 200
    logs = res.json()
    assert isinstance(logs, list)
    assert len(logs) >= 1


def test_query_pipeline_and_report_downloads(client):
    # 1. Execute analytical query
    res = client.post(
        "/api/v1/queries",
        json={"question": "What is the total sales amount in the sales_orders table?"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCEEDED"
    query_id = data["query_id"]
    assert query_id.startswith("req-")

    # 2. Check query history
    res_hist = client.get("/api/v1/queries/history")
    assert res_hist.status_code == 200
    history = res_hist.json()
    assert any(h["query_id"] == query_id for h in history)

    # 3. Download PDF Report
    res_pdf = client.get(f"/api/v1/reports/{query_id}/download?format=pdf")
    assert res_pdf.status_code == 200
    assert "application/pdf" in res_pdf.headers.get("content-type", "")
    assert len(res_pdf.content) > 0

    # 4. Download Excel Report
    res_excel = client.get(f"/api/v1/reports/{query_id}/download?format=excel")
    assert res_excel.status_code == 200
    assert "spreadsheetml.sheet" in res_excel.headers.get("content-type", "")
    assert len(res_excel.content) > 0

    # 5. Invalid format returns 400
    res_bad = client.get(f"/api/v1/reports/{query_id}/download?format=invalid_fmt")
    assert res_bad.status_code == 400

