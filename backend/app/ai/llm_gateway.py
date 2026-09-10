import time
from typing import Any, Dict, List, Optional
from app.core.config import settings
from app.ai.schemas.llm_schemas import LLMMessage, LLMResponse
from app.ai.providers.mock_provider import MockLLMProvider
from app.ai.providers.openai_provider import OpenAIProvider
from app.ai.providers.gemini_provider import GeminiProvider
from app.ai.providers.anthropic_provider import AnthropicProvider
from app.ai.key_detector import KNOWN_PROVIDERS, detect_provider_from_key


class LLMGateway:
    def __init__(self, provider_name: Optional[str] = None, model: Optional[str] = None):
        self.provider_name = (provider_name or settings.LLM_PROVIDER).lower()
        self.model = model or settings.LLM_MODEL
        self.providers_vault: Dict[str, Dict[str, Any]] = {}
        self.collaboration_config: Dict[str, Any] = {
            "enabled": False,
            "roles": {
                "sql_generator": None,
                "sql_reviewer": None,
                "insight_generator": None,
            },
        }
        self._init_default_vault()

    def _init_default_vault(self):
        """Pre-populates vault from environment variables if present."""
        if settings.GEMINI_API_KEY:
            self.register_vault_key(
                provider_id="gemini_default",
                provider_type="gemini",
                name="Google Gemini (Primary)",
                api_key=settings.GEMINI_API_KEY,
                model=getattr(settings, "GEMINI_MODEL", "gemini-flash-latest"),
                base_url=None,
                is_active=(self.provider_name in ["gemini", "google"]),
            )
        if settings.OPENAI_API_KEY:
            self.register_vault_key(
                provider_id="openai_default",
                provider_type="openai",
                name="OpenAI (Primary)",
                api_key=settings.OPENAI_API_KEY,
                model=settings.LLM_MODEL or "gpt-4o-mini",
                base_url="https://api.openai.com/v1",
                is_active=(self.provider_name == "openai"),
            )

    def register_vault_key(
        self,
        provider_id: str,
        provider_type: str,
        name: str,
        api_key: str,
        model: str,
        base_url: Optional[str] = None,
        is_active: bool = False,
    ) -> Dict[str, Any]:
        """Registers or updates an API key in the multi-provider vault."""
        clean_key = api_key.strip() if api_key else ""
        clean_type = provider_type.lower().strip()

        # If base_url is not provided, look up default for known providers
        resolved_base_url = base_url
        if not resolved_base_url:
            matched = next((p for p in KNOWN_PROVIDERS if p["id"] == clean_type), None)
            if matched and matched.get("base_url"):
                resolved_base_url = matched["base_url"]

        entry = {
            "id": provider_id,
            "provider": clean_type,
            "name": name or f"{clean_type.capitalize()} ({model})",
            "api_key": clean_key,
            "model": model,
            "base_url": resolved_base_url,
            "is_active": is_active,
            "created_at": time.time(),
        }

        if is_active:
            for k, v in self.providers_vault.items():
                v["is_active"] = False
            self.provider_name = clean_type
            self.model = model
            if clean_type in ["gemini", "google"]:
                settings.GEMINI_API_KEY = clean_key
                settings.LLM_PROVIDER = clean_type
                settings.LLM_MODEL = model
            elif clean_type == "openai":
                settings.OPENAI_API_KEY = clean_key
                settings.LLM_PROVIDER = clean_type
                settings.LLM_MODEL = model

        self.providers_vault[provider_id] = entry
        return entry

    def delete_vault_key(self, provider_id: str) -> bool:
        """Deletes a provider key from the vault."""
        if provider_id in self.providers_vault:
            entry = self.providers_vault.pop(provider_id)
            if entry.get("is_active"):
                self.provider_name = "mock"
                self.model = "deterministic-v1"
            # Unlink from collaboration roles
            for role, pid in list(self.collaboration_config["roles"].items()):
                if pid == provider_id:
                    self.collaboration_config["roles"][role] = None
            return True
        return False

    def list_vault_keys(self, mask: bool = True) -> List[Dict[str, Any]]:
        """Lists all registered keys with optional masking."""
        result = []
        for pid, entry in self.providers_vault.items():
            masked_key = entry["api_key"]
            if mask and entry["api_key"]:
                raw = entry["api_key"]
                if len(raw) <= 10:
                    masked_key = f"{raw[:3]}...{raw[-2:]}"
                else:
                    masked_key = f"{raw[:8]}...{raw[-4:]}"
            result.append({
                "id": entry["id"],
                "provider": entry["provider"],
                "name": entry["name"],
                "api_key_masked": masked_key if mask else entry["api_key"],
                "model": entry["model"],
                "base_url": entry["base_url"],
                "is_active": entry.get("is_active", False),
                "created_at": entry.get("created_at", 0),
            })
        return result

    def get_vault_key(self, provider_id: str) -> Optional[Dict[str, Any]]:
        return self.providers_vault.get(provider_id)

    def set_active_provider(self, provider_id: str) -> bool:
        if provider_id not in self.providers_vault:
            return False
        for k, v in self.providers_vault.items():
            v["is_active"] = (k == provider_id)
        entry = self.providers_vault[provider_id]
        self.provider_name = entry["provider"]
        self.model = entry["model"]
        settings.LLM_PROVIDER = entry["provider"]
        settings.LLM_MODEL = entry["model"]
        if entry["provider"] in ["gemini", "google"]:
            settings.GEMINI_API_KEY = entry["api_key"]
        elif entry["provider"] == "openai":
            settings.OPENAI_API_KEY = entry["api_key"]
        return True

    def configure(
        self,
        provider_name: Optional[str] = None,
        model: Optional[str] = None,
        gemini_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
    ):
        """Dynamically reconfigures active LLM provider, model, and API keys (backward compatible)."""
        if provider_name:
            self.provider_name = provider_name.lower()
            settings.LLM_PROVIDER = self.provider_name
        if model:
            self.model = model
            settings.LLM_MODEL = model
            if self.provider_name in ["gemini", "google"]:
                settings.GEMINI_MODEL = model
        if gemini_api_key is not None:
            settings.GEMINI_API_KEY = gemini_api_key
            if gemini_api_key:
                self.register_vault_key("gemini_default", "gemini", "Google Gemini", gemini_api_key, self.model or "gemini-flash-latest")
            else:
                self.delete_vault_key("gemini_default")
        if openai_api_key is not None:
            settings.OPENAI_API_KEY = openai_api_key
            if openai_api_key:
                self.register_vault_key("openai_default", "openai", "OpenAI", openai_api_key, self.model or "gpt-4o-mini", "https://api.openai.com/v1")
            else:
                self.delete_vault_key("openai_default")

    def configure_collaboration(self, enabled: bool, roles: Optional[Dict[str, Optional[str]]] = None) -> Dict[str, Any]:
        """Sets collaboration state and assigned roles."""
        self.collaboration_config["enabled"] = enabled
        if roles:
            for role_name in ["sql_generator", "sql_reviewer", "insight_generator"]:
                if role_name in roles:
                    self.collaboration_config["roles"][role_name] = roles[role_name]
        return self.collaboration_config

    def is_collaboration_enabled(self) -> bool:
        """Returns True if collaboration is turned on and configured."""
        return bool(self.collaboration_config.get("enabled", False))

    def get_provider(
        self,
        override_provider: Optional[str] = None,
        override_model: Optional[str] = None,
        override_api_key: Optional[str] = None,
        override_base_url: Optional[str] = None,
    ):
        """Universal provider resolver supporting any AI provider."""
        provider = (override_provider or self.provider_name).lower()
        model = override_model or self.model
        base_url = override_base_url

        if provider in ["gemini", "google"]:
            key = override_api_key or settings.GEMINI_API_KEY
            return GeminiProvider(api_key=key, model=model)
        elif provider == "anthropic":
            key = override_api_key
            return AnthropicProvider(api_key=key, model=model, base_url=base_url)
        elif provider in ["mock", "offline", "deterministic"]:
            return MockLLMProvider(model=model)
        else:
            # Universal OpenAI-compatible client (OpenAI, DeepSeek, Groq, OpenRouter, Mistral, Custom)
            key = override_api_key or (settings.OPENAI_API_KEY if provider == "openai" else None)
            if not base_url:
                matched = next((p for p in KNOWN_PROVIDERS if p["id"] == provider), None)
                if matched and matched.get("base_url"):
                    base_url = matched["base_url"]
            return OpenAIProvider(api_key=key, model=model, base_url=base_url)

    def get_provider_by_role(self, role: str):
        """
        Retrieves the provider assigned to a collaboration role.
        Falls back to default get_provider() if role is not configured or vault entry not found.
        """
        if self.is_collaboration_enabled():
            role_target = self.collaboration_config.get("roles", {}).get(role)
            if role_target:
                # Target could be a provider_id in vault
                if role_target in self.providers_vault:
                    entry = self.providers_vault[role_target]
                    return self.get_provider(
                        override_provider=entry["provider"],
                        override_model=entry["model"],
                        override_api_key=entry["api_key"],
                        override_base_url=entry["base_url"],
                    )
                # Or a provider type string directly
                return self.get_provider(override_provider=role_target)

        # Fallback to default
        return self.get_provider()

    def get_provider_info_by_role(self, role: str) -> Dict[str, str]:
        """Returns descriptive name, provider type, and model for a collaboration role."""
        if self.is_collaboration_enabled():
            role_target = self.collaboration_config.get("roles", {}).get(role)
            if role_target and role_target in self.providers_vault:
                entry = self.providers_vault[role_target]
                return {
                    "role": role,
                    "provider": entry["provider"],
                    "model": entry["model"],
                    "name": entry["name"],
                }
        return {
            "role": role,
            "provider": self.provider_name,
            "model": self.model,
            "name": f"{self.provider_name.capitalize()} ({self.model})",
        }

    def generate(
        self,
        messages: List[LLMMessage],
        tools: List[Dict[str, Any]] = None,
        temperature: float = 0.0,
        role: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> LLMResponse:
        """Generates LLM response, enforcing Token Governance (RPM & budget quota) and routing to provider."""
        from app.core.tenant import get_tenant_context
        from app.security.token_governance import (
            token_governance,
            RateLimitExceededException,
            TokenBudgetExceededException,
        )

        t_id = tenant_id
        if not t_id:
            ctx = get_tenant_context()
            t_id = ctx.tenant_id if ctx else "tenant-acme"

        # 1. Rate Limit Check (Sliding Window RPM)
        allowed_rpm, current_rpm = token_governance.check_rate_limit(t_id)
        if not allowed_rpm:
            raise RateLimitExceededException(
                f"Rate limit exceeded: Tenant '{t_id}' reached {current_rpm} requests per minute (limit: {token_governance.rpm_limit} RPM)."
            )

        # 2. Token Budget Check
        total_prompt_chars = sum(len(m.content) for m in messages if m.content)
        estimated_tokens = max(50, total_prompt_chars // 4)
        budget_ok, budget_stats = token_governance.check_and_deduct_tokens(
            tenant_id=t_id,
            estimated_tokens=estimated_tokens,
            estimated_cost_usd=round(estimated_tokens * 0.000002, 6),
        )
        if not budget_ok:
            raise TokenBudgetExceededException(
                f"Token budget exceeded: Tenant '{t_id}' reached daily quota ({budget_stats.get('used_tokens', 0)}/{token_governance.daily_token_limit} tokens)."
            )

        provider = self.get_provider_by_role(role) if role else self.get_provider()
        response = provider.generate(messages=messages, tools=tools, temperature=temperature)

        # 3. Account for response completion tokens
        if response and response.content:
            completion_tokens = max(10, len(response.content) // 4)
            token_governance.check_and_deduct_tokens(
                tenant_id=t_id,
                estimated_tokens=completion_tokens,
                estimated_cost_usd=round(completion_tokens * 0.000002, 6),
            )

        return response


llm_gateway = LLMGateway()
