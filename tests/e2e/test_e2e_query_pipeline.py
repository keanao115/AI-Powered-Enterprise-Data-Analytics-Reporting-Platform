import pytest
from app.core.tenant import TenantContext
from app.ai.agent.analyst_agent import analyst_agent
from seed.seed_data import seed_synthetic_analytics_database


from app.core.database import get_analytics_db_path


@pytest.fixture(scope="module", autouse=True)
def setup_demo_db():
    seed_synthetic_analytics_database(get_analytics_db_path())


def test_e2e_analyst_agent_pipeline():
    ctx = TenantContext(
        tenant_id="tenant-acme",
        organization_id="org-acme-corp",
        workspace_id="ws-sales-analytics",
        user_id="user-analyst",
        user_role="ANALYST",
        authorized_regions=["US", "EU", "APAC"],
        authorized_departments=["Sales", "Executive"],
    )

    question = "Find the top 10 products by revenue"
    state = analyst_agent.execute_pipeline(question, ctx, dataset_id="ecommerce_olist")

    assert state.request_id.startswith("req-")
    assert state.generated_sql is not None
    assert state.validated_sql is not None
    assert state.data_quality["quality_score"] > 50.0
    assert len(state.analytical_results["rows"]) > 0
    assert len(state.claims) > 0
    assert state.grounding_status == "PASSED"
