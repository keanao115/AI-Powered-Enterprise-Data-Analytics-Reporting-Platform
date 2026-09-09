import os
import time
import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.core.config import settings
from app.ai.llm_gateway import llm_gateway
from app.ai.schemas.llm_schemas import LLMMessage
from app.ai.key_detector import KNOWN_PROVIDERS, detect_provider_from_key, DetectedProviderInfo

router = APIRouter(prefix="/settings", tags=["Settings & API Configuration"])


AVAILABLE_PROVIDERS = [
    {
        "id": p["id"],
        "name": p["name"],
        "description": p["description"],
        "default_model": p["default_model"],
        "models": p["models"],
        "base_url": p.get("base_url"),
        "key_required": p["id"] != "mock",
        "key_field": f"{p['id']}_api_key" if p["id"] in ["gemini", "openai"] else "api_key",
    }
    for p in KNOWN_PROVIDERS
]


def mask_key(key: Optional[str]) -> Optional[str]:
    """Masks secret API keys for safe UI inspection (e.g. AQ.Ab8R...c0rg)."""
    if not key:
        return None
    cleaned = key.strip()
    if len(cleaned) <= 10:
        return f"{cleaned[:3]}...{cleaned[-2:]}"
    return f"{cleaned[:8]}...{cleaned[-4:]}"


def update_env_file(updates: Dict[str, str]):
    """
    Safely persists updated environment variables to .env on disk.
    Preserves comments and unrelated configuration variables across all local .env files.
    """
    env_paths = [
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".env")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env")),
    ]
    target_files = [p for p in env_paths if os.path.exists(p)]
    if not target_files:
        target_files = [env_paths[0]]

    for target_env in set(target_files):
        lines = []
        if os.path.exists(target_env):
            with open(target_env, "r", encoding="utf-8") as f:
                lines = f.readlines()

        updated_keys = set()
        new_lines = []

        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and "=" in stripped:
                k = stripped.split("=", 1)[0].strip()
                if k in updates:
                    new_lines.append(f"{k}={updates[k]}\n")
                    updated_keys.add(k)
                    continue
            new_lines.append(line)

        # Append any keys that didn't exist previously
        for k, v in updates.items():
            if k not in updated_keys:
                new_lines.append(f"{k}={v}\n")

        with open(target_env, "w", encoding="utf-8") as f:
            f.writelines(new_lines)


class LLMConfigResponse(BaseModel):
    provider: str
    model: str
    gemini_api_key_configured: bool
    gemini_api_key_masked: Optional[str]
    openai_api_key_configured: bool
    openai_api_key_masked: Optional[str]
    available_providers: List[Dict[str, Any]]


class UpdateLLMConfigRequest(BaseModel):
    provider: Optional[str] = Field(None, description="LLM provider: gemini, openai, deepseek, groq, anthropic, openrouter, mock, custom")
    model: Optional[str] = Field(None, description="Model identifier")
    gemini_api_key: Optional[str] = Field(None, description="Google Gemini API Key")
    openai_api_key: Optional[str] = Field(None, description="OpenAI API Key")
    persist_to_env: bool = Field(default=True, description="Save changes safely to local .env")


class DetectKeyRequest(BaseModel):
    key: str = Field(..., description="API key to analyze and detect target provider")


class VaultKeyRequest(BaseModel):
    id: Optional[str] = Field(None, description="Unique key identifier, auto-generated if omitted")
    provider: str = Field(..., description="Provider identifier (gemini, openai, deepseek, etc.)")
    name: Optional[str] = Field(None, description="Human-readable label for this key")
    api_key: str = Field(..., description="The raw API key")
    model: str = Field(..., description="The target model for this key")
    base_url: Optional[str] = Field(None, description="Optional custom base URL")
    is_active: bool = Field(default=False, description="Set as the current active system provider")


class CollaborationRoles(BaseModel):
    sql_generator: Optional[str] = Field(None, description="Provider ID or type for SQL generation")
    sql_reviewer: Optional[str] = Field(None, description="Provider ID or type for SQL review/optimization")
    insight_generator: Optional[str] = Field(None, description="Provider ID or type for executive insights")


class CollaborationConfigRequest(BaseModel):
    enabled: bool = Field(..., description="Enable multi-model collaborative analytics")
    roles: Optional[CollaborationRoles] = None


class TestLLMConnectionRequest(BaseModel):
    provider: str = Field(..., description="Provider to test")
    model: Optional[str] = Field(None, description="Model identifier")
    api_key: Optional[str] = Field(None, description="Candidate API Key to test")
    base_url: Optional[str] = Field(None, description="Optional custom base URL")


class TestLLMConnectionResponse(BaseModel):
    success: bool
    provider: str
    model: str
    latency_ms: float
    message: str
    sample_output: Optional[str] = None


@router.get("/llm", response_model=LLMConfigResponse)
async def get_llm_settings():
    """Returns current active LLM provider and safely masked API key indicators."""
    return LLMConfigResponse(
        provider=settings.LLM_PROVIDER,
        model=settings.LLM_MODEL,
        gemini_api_key_configured=bool(settings.GEMINI_API_KEY),
        gemini_api_key_masked=mask_key(settings.GEMINI_API_KEY),
        openai_api_key_configured=bool(settings.OPENAI_API_KEY),
        openai_api_key_masked=mask_key(settings.OPENAI_API_KEY),
        available_providers=AVAILABLE_PROVIDERS,
    )


@router.post("/llm", response_model=LLMConfigResponse)
async def update_llm_settings(req: UpdateLLMConfigRequest):
    """
    Updates active LLM configuration in memory and optionally writes to local .env.
    Changes take effect immediately on subsequent queries.
    """
    provider = (req.provider or settings.LLM_PROVIDER).lower()
    model = req.model or settings.LLM_MODEL

    env_updates: Dict[str, str] = {}
    if req.provider:
        env_updates["LLM_PROVIDER"] = provider
    if req.model:
        env_updates["LLM_MODEL"] = model

    gem_key = req.gemini_api_key.strip() if req.gemini_api_key is not None else None
    if gem_key is not None:
        if gem_key:
            env_updates["GEMINI_API_KEY"] = gem_key
            settings.GEMINI_API_KEY = gem_key
        else:
            env_updates["GEMINI_API_KEY"] = ""
            settings.GEMINI_API_KEY = None

    oa_key = req.openai_api_key.strip() if req.openai_api_key is not None else None
    if oa_key is not None:
        if oa_key:
            env_updates["OPENAI_API_KEY"] = oa_key
            settings.OPENAI_API_KEY = oa_key
        else:
            env_updates["OPENAI_API_KEY"] = ""
            settings.OPENAI_API_KEY = None

    llm_gateway.configure(
        provider_name=provider,
        model=model,
        gemini_api_key=settings.GEMINI_API_KEY,
        openai_api_key=settings.OPENAI_API_KEY,
    )

    if req.persist_to_env and env_updates:
        try:
            update_env_file(env_updates)
        except Exception as e:
            print(f"[Settings] Warning: Failed to persist to .env file: {e}")

    return LLMConfigResponse(
        provider=settings.LLM_PROVIDER,
        model=settings.LLM_MODEL,
        gemini_api_key_configured=bool(settings.GEMINI_API_KEY),
        gemini_api_key_masked=mask_key(settings.GEMINI_API_KEY),
        openai_api_key_configured=bool(settings.OPENAI_API_KEY),
        openai_api_key_masked=mask_key(settings.OPENAI_API_KEY),
        available_providers=AVAILABLE_PROVIDERS,
    )


@router.post("/detect-key", response_model=DetectedProviderInfo)
async def detect_key(req: DetectKeyRequest):
    """
    Analyzes an input API key to identify provider type, recommended models, and default base URL.
    """
    return detect_provider_from_key(req.key)


@router.get("/vault")
async def get_vault_keys():
    """
    Returns all registered API keys in the multi-provider vault with masked credentials.
    """
    return {
        "keys": llm_gateway.list_vault_keys(mask=True),
        "total": len(llm_gateway.providers_vault),
        "active_provider": llm_gateway.provider_name,
        "active_model": llm_gateway.model,
    }


@router.post("/vault")
async def add_or_update_vault_key(req: VaultKeyRequest):
    """
    Adds or updates an API key in the multi-provider vault.
    """
    key_id = req.id or f"{req.provider}_{uuid.uuid4().hex[:6]}"
    saved = llm_gateway.register_vault_key(
        provider_id=key_id,
        provider_type=req.provider,
        name=req.name or f"{req.provider.capitalize()} ({req.model})",
        api_key=req.api_key,
        model=req.model,
        base_url=req.base_url,
        is_active=req.is_active,
    )
    return {
        "success": True,
        "message": f"Successfully registered key '{saved['name']}' in vault.",
        "key": {
            "id": saved["id"],
            "provider": saved["provider"],
            "name": saved["name"],
            "api_key_masked": mask_key(saved["api_key"]),
            "model": saved["model"],
            "base_url": saved["base_url"],
            "is_active": saved["is_active"],
        },
    }


@router.delete("/vault/{provider_id}")
async def delete_vault_key(provider_id: str):
    """
    Deletes an API key from the multi-provider vault.
    """
    deleted = llm_gateway.delete_vault_key(provider_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Key with ID '{provider_id}' not found in vault.",
        )
    return {
        "success": True,
        "message": f"Key '{provider_id}' removed from vault.",
    }


@router.post("/vault/{provider_id}/activate")
async def activate_vault_key(provider_id: str):
    """
    Sets a specific vault key as the active system provider for primary inference.
    """
    activated = llm_gateway.set_active_provider(provider_id)
    if not activated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Key with ID '{provider_id}' not found in vault.",
        )
    return {
        "success": True,
        "message": f"Provider key '{provider_id}' is now active.",
        "active_provider": llm_gateway.provider_name,
        "active_model": llm_gateway.model,
    }


@router.get("/collaboration")
async def get_collaboration_settings():
    """
    Returns the current multi-model collaboration configuration and role participants.
    """
    config = llm_gateway.get_collaboration_config()
    roles = config.get("roles", {})
    participants = [
        llm_gateway.get_provider_info_by_role("sql_generator"),
        llm_gateway.get_provider_info_by_role("sql_reviewer"),
        llm_gateway.get_provider_info_by_role("insight_generator"),
    ]
    return {
        "enabled": config.get("enabled", False),
        "roles": roles,
        "participants": participants,
        "vault_keys": llm_gateway.list_vault_keys(mask=True),
    }


@router.post("/collaboration")
async def update_collaboration_settings(req: CollaborationConfigRequest):
    """
    Configures multi-model collaboration pipeline roles and enabled flag.
    """
    roles_dict = None
    if req.roles:
        roles_dict = {
            "sql_generator": req.roles.sql_generator,
            "sql_reviewer": req.roles.sql_reviewer,
            "insight_generator": req.roles.insight_generator,
        }
    updated = llm_gateway.configure_collaboration(enabled=req.enabled, roles=roles_dict)
    participants = [
        llm_gateway.get_provider_info_by_role("sql_generator"),
        llm_gateway.get_provider_info_by_role("sql_reviewer"),
        llm_gateway.get_provider_info_by_role("insight_generator"),
    ]
    return {
        "success": True,
        "message": "Collaboration settings updated successfully.",
        "config": updated,
        "participants": participants,
    }


@router.post("/test-llm", response_model=TestLLMConnectionResponse)
async def test_llm_connection(req: TestLLMConnectionRequest):
    """
    Sends a test request to the specified LLM provider and measures latency and connectivity.
    Supports any AI model or custom OpenAI-compatible endpoint.
    """
    provider_name = req.provider.lower()
    target_model = req.model or settings.LLM_MODEL
    api_key = req.api_key.strip() if req.api_key else None
    base_url = req.base_url.strip() if req.base_url else None

    # Fallback to current settings key if not passed
    if not api_key:
        if provider_name in ["gemini", "google"]:
            api_key = settings.GEMINI_API_KEY
        elif provider_name == "openai":
            api_key = settings.OPENAI_API_KEY

    # Check key requirement for cloud providers (offline mock doesn't need a key)
    if provider_name not in ["mock", "offline", "deterministic"] and not api_key:
        return TestLLMConnectionResponse(
            success=False,
            provider=provider_name,
            model=target_model,
            latency_ms=0.0,
            message=f"Missing API Key for provider '{provider_name}'. Please enter an API key to test.",
        )

    start_time = time.time()
    try:
        provider = llm_gateway.get_provider(
            override_provider=provider_name,
            override_model=target_model,
            override_api_key=api_key,
            override_base_url=base_url,
        )

        test_msg = [
            LLMMessage(role="system", content="You are a health check agent. Output 'READY' followed by 1 sentence explaining that DuckDB analytics is online."),
            LLMMessage(role="user", content="Ping healthcheck"),
        ]

        response = provider.generate(test_msg, temperature=0.0)
        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        return TestLLMConnectionResponse(
            success=True,
            provider=provider_name,
            model=response.model or target_model,
            latency_ms=elapsed_ms,
            message="Connection succeeded. Provider responded with valid inference output.",
            sample_output=response.content[:200].strip(),
        )
    except Exception as e:
        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        return TestLLMConnectionResponse(
            success=False,
            provider=provider_name,
            model=target_model,
            latency_ms=elapsed_ms,
            message=f"Connection failed: {str(e)}",
        )
