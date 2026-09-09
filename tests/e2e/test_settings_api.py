import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.ai.llm_gateway import llm_gateway

client = TestClient(app)


def test_get_llm_settings():
    res = client.get("/api/v1/settings/llm")
    assert res.status_code == 200
    data = res.json()
    assert "provider" in data
    assert "model" in data
    assert "available_providers" in data
    assert len(data["available_providers"]) >= 3
    provider_ids = [p["id"] for p in data["available_providers"]]
    assert "gemini" in provider_ids
    assert "openai" in provider_ids
    assert "mock" in provider_ids


def test_update_llm_settings():
    original_provider = settings.LLM_PROVIDER
    original_model = settings.LLM_MODEL

    try:
        # Update to mock provider with custom model
        res = client.post(
            "/api/v1/settings/llm",
            json={
                "provider": "mock",
                "model": "deterministic-v1",
                "persist_to_env": False,
            }
        )
        assert res.status_code == 200
        data = res.json()
        assert data["provider"] == "mock"
        assert data["model"] == "deterministic-v1"
        assert llm_gateway.provider_name == "mock"

        # Update to gemini provider
        res2 = client.post(
            "/api/v1/settings/llm",
            json={
                "provider": "gemini",
                "model": "gemini-flash-latest",
                "persist_to_env": False,
            }
        )
        assert res2.status_code == 200
        assert res2.json()["provider"] == "gemini"
        assert llm_gateway.provider_name == "gemini"
    finally:
        # Restore original
        llm_gateway.configure(provider_name=original_provider, model=original_model)


def test_test_llm_connection_mock():
    res = client.post(
        "/api/v1/settings/test-llm",
        json={
            "provider": "mock",
            "model": "deterministic-v1",
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["provider"] == "mock"
    assert "latency_ms" in data


def test_test_llm_connection_missing_key():
    res = client.post(
        "/api/v1/settings/test-llm",
        json={
            "provider": "openai",
            "model": "gpt-4o",
            "api_key": "",
        }
    )
    assert res.status_code == 200
    data = res.json()
    # If no OpenAI key configured, should return friendly validation error
    if not settings.OPENAI_API_KEY:
        assert data["success"] is False
        assert "Missing API Key" in data["message"]


def test_gemini_blank_key_requires_manual_input():
    original_gemini_key = settings.GEMINI_API_KEY
    try:
        # 1. Clear key to verify blank default behavior
        settings.GEMINI_API_KEY = None
        llm_gateway.configure(gemini_api_key=None)

        res = client.get("/api/v1/settings/llm")
        assert res.status_code == 200
        data = res.json()
        assert data["gemini_api_key_configured"] is False
        assert data["gemini_api_key_masked"] is None

        # 2. Connection test without key must fail with friendly prompt
        res_test = client.post(
            "/api/v1/settings/test-llm",
            json={
                "provider": "gemini",
                "model": "gemini-flash-latest",
                "api_key": "",
            }
        )
        assert res_test.status_code == 200
        test_data = res_test.json()
        assert test_data["success"] is False
        assert "Missing API Key" in test_data["message"]

        # 3. Simulate user manually entering key in settings
        res_save = client.post(
            "/api/v1/settings/llm",
            json={
                "provider": "gemini",
                "gemini_api_key": "AQ.Ab8RN6_manual_key_test",
                "persist_to_env": False,
            }
        )
        assert res_save.status_code == 200
        saved_data = res_save.json()
        assert saved_data["gemini_api_key_configured"] is True
        assert "AQ.Ab8RN" in (saved_data["gemini_api_key_masked"] or "")

        # 4. User clears key again
        res_clear = client.post(
            "/api/v1/settings/llm",
            json={
                "provider": "gemini",
                "gemini_api_key": "",
                "persist_to_env": False,
            }
        )
        assert res_clear.status_code == 200
        assert res_clear.json()["gemini_api_key_configured"] is False
    finally:
        # Restore
        settings.GEMINI_API_KEY = original_gemini_key
        llm_gateway.configure(gemini_api_key=original_gemini_key)


def test_revoke_openai_and_gemini_api_key():
    orig_gem = settings.GEMINI_API_KEY
    orig_oa = settings.OPENAI_API_KEY
    try:
        # 1. Configure both keys
        client.post(
            "/api/v1/settings/llm",
            json={
                "gemini_api_key": "AQ.Ab8RN6_gem_key",
                "openai_api_key": "sk-proj-test-oa-key",
                "persist_to_env": False,
            }
        )
        status1 = client.get("/api/v1/settings/llm").json()
        assert status1["gemini_api_key_configured"] is True
        assert status1["openai_api_key_configured"] is True

        # 2. Revoke Gemini key
        res_rev_gem = client.post(
            "/api/v1/settings/llm",
            json={
                "gemini_api_key": "",
                "persist_to_env": False,
            }
        )
        assert res_rev_gem.status_code == 200
        data_rev_gem = res_rev_gem.json()
        assert data_rev_gem["gemini_api_key_configured"] is False
        assert data_rev_gem["openai_api_key_configured"] is True

        # 3. Revoke OpenAI key
        res_rev_oa = client.post(
            "/api/v1/settings/llm",
            json={
                "openai_api_key": "",
                "persist_to_env": False,
            }
        )
        assert res_rev_oa.status_code == 200
        data_rev_oa = res_rev_oa.json()
        assert data_rev_oa["gemini_api_key_configured"] is False
        assert data_rev_oa["openai_api_key_configured"] is False
    finally:
        settings.GEMINI_API_KEY = orig_gem
        settings.OPENAI_API_KEY = orig_oa
        llm_gateway.configure(gemini_api_key=orig_gem, openai_api_key=orig_oa)


def test_auto_detect_api_key_patterns():
    # 1. Gemini (AIzaSy or AQ.)
    r1 = client.post("/api/v1/settings/detect-key", json={"key": "AQ.Ab8RN6Ikiq5fZP6sWDfLfLo6yVHbtYyMwqVKC5igm_-XALc0rg"})
    assert r1.status_code == 200
    d1 = r1.json()
    assert d1["provider_id"] == "gemini"
    assert d1["confidence"] == "HIGH"
    assert "gemini-flash-latest" in d1["recommended_models"]

    # 2. Anthropic Claude
    r2 = client.post("/api/v1/settings/detect-key", json={"key": "sk-ant-api03-abcdef123456789"})
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2["provider_id"] == "anthropic"
    assert d2["confidence"] == "HIGH"
    assert "claude-3-5-sonnet-20241022" in d2["recommended_models"]

    # 3. Groq
    r3 = client.post("/api/v1/settings/detect-key", json={"key": "gsk_1234567890abcdef"})
    assert r3.status_code == 200
    d3 = r3.json()
    assert d3["provider_id"] == "groq"
    assert d3["confidence"] == "HIGH"

    # 4. OpenRouter
    r4 = client.post("/api/v1/settings/detect-key", json={"key": "sk-or-v1-abcdef123456789"})
    assert r4.status_code == 200
    d4 = r4.json()
    assert d4["provider_id"] == "openrouter"
    assert d4["confidence"] == "HIGH"

    # 5. DeepSeek
    r5 = client.post("/api/v1/settings/detect-key", json={"key": "dsk-abcdef123456789"})
    assert r5.status_code == 200
    d5 = r5.json()
    assert d5["provider_id"] == "deepseek"
    assert d5["confidence"] == "HIGH"

    # 6. Mock / Deterministic
    r6 = client.post("/api/v1/settings/detect-key", json={"key": "mock"})
    assert r6.status_code == 200
    d6 = r6.json()
    assert d6["provider_id"] == "mock"
    assert d6["confidence"] == "HIGH"

    # 7. Custom fallback
    r7 = client.post("/api/v1/settings/detect-key", json={"key": "my-custom-endpoint-key-999"})
    assert r7.status_code == 200
    d7 = r7.json()
    assert d7["provider_id"] == "custom"


def test_vault_crud_and_activation():
    # 1. Add key to vault
    res_add = client.post(
        "/api/v1/settings/vault",
        json={
            "id": "deepseek_test_key",
            "provider": "deepseek",
            "name": "DeepSeek Test",
            "api_key": "dsk-test-secret-1234567890",
            "model": "deepseek-chat",
            "is_active": False,
        }
    )
    assert res_add.status_code == 200
    add_data = res_add.json()
    assert add_data["success"] is True
    assert "dsk-test" in add_data["key"]["api_key_masked"]

    # 2. Get vault list
    res_list = client.get("/api/v1/settings/vault")
    assert res_list.status_code == 200
    vault_list = res_list.json()
    key_ids = [k["id"] for k in vault_list["keys"]]
    assert "deepseek_test_key" in key_ids

    # 3. Activate key
    res_act = client.post("/api/v1/settings/vault/deepseek_test_key/activate")
    assert res_act.status_code == 200
    assert res_act.json()["active_provider"] == "deepseek"
    assert llm_gateway.provider_name == "deepseek"

    # 4. Delete key
    res_del = client.delete("/api/v1/settings/vault/deepseek_test_key")
    assert res_del.status_code == 200
    assert res_del.json()["success"] is True

    # Verify deletion
    res_list2 = client.get("/api/v1/settings/vault")
    assert "deepseek_test_key" not in [k["id"] for k in res_list2.json()["keys"]]


def test_multi_model_collaboration_settings_and_pipeline():
    # 1. Register two keys in vault
    client.post(
        "/api/v1/settings/vault",
        json={
            "id": "model_a_sql",
            "provider": "mock",
            "name": "Model A (SQL Gen)",
            "api_key": "mock",
            "model": "deterministic-v1",
        }
    )
    client.post(
        "/api/v1/settings/vault",
        json={
            "id": "model_b_review",
            "provider": "mock",
            "name": "Model B (SQL Reviewer)",
            "api_key": "mock",
            "model": "deterministic-v1",
        }
    )

    # 2. Configure collaboration
    res_collab = client.post(
        "/api/v1/settings/collaboration",
        json={
            "enabled": True,
            "roles": {
                "sql_generator": "model_a_sql",
                "sql_reviewer": "model_b_review",
                "insight_generator": "model_a_sql",
            }
        }
    )
    assert res_collab.status_code == 200
    collab_data = res_collab.json()
    assert collab_data["config"]["enabled"] is True
    assert len(collab_data["participants"]) == 3

    # 3. Execute query through analyst agent
    from app.ai.agent.analyst_agent import analyst_agent
    from app.core.tenant import TenantContext
    ctx = TenantContext(tenant_id="tenant_collab_test", user_id="u_collab")

    state = analyst_agent.execute_pipeline("分析巴西電商中銷售額最高的前 5 大產品類別", ctx, dataset_id="ecommerce_olist")
    assert state.grounding_status == "PASSED"
    assert state.collaboration_info is not None
    assert state.collaboration_info["enabled"] is True

    # Verify that SQL_COLLABORATIVE_REVIEW step was executed
    step_names = [s["step"] for s in state.execution_steps]
    assert "SQL_GENERATION" in step_names
    assert "SQL_COLLABORATIVE_REVIEW" in step_names

    # Clean up collaboration
    client.post("/api/v1/settings/collaboration", json={"enabled": False})



