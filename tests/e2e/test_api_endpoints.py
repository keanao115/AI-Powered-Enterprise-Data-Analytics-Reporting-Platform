import pytest
from fastapi.testclient import TestClient
from app.main import app
from seed.seed_data import seed_synthetic_analytics_database

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    seed_synthetic_analytics_database("analytics_demo.duckdb")

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
        "ecommerce_olist", "transportation_nyc_taxi", "airline_bts_ontime",
        "healthcare_mimic_iv", "safety_chicago_crimes", "financial_sec_markets"
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

def test_audit_logs_endpoint(client):
    res = client.get("/api/v1/audit")
    assert res.status_code == 200
    logs = res.json()
    assert isinstance(logs, list)
    assert len(logs) >= 3
