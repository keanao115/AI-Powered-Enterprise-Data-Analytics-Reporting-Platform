import os
import time
from typing import Any, Dict, List, Optional

import httpx

from app.ai.resilience import CircuitBreaker
from app.ai.schemas.llm_schemas import LLMMessage, LLMResponse
from app.core.config import settings

# Shared module-level circuit breaker instance for Gemini
gemini_circuit_breaker = CircuitBreaker(
    name="GeminiAPI", failure_threshold=2, recovery_timeout=60.0
)


class GeminiProvider:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = (
            api_key
            or settings.GEMINI_API_KEY
            or os.environ.get("GEMINI_API_KEY")
            or os.environ.get("GOOGLE_API_KEY")
        )
        self.model = (
            model or getattr(settings, "GEMINI_MODEL", "gemini-3.6-flash") or "gemini-3.6-flash"
        )

    def generate(
        self,
        messages: List[LLMMessage],
        tools: List[Dict[str, Any]] = None,
        temperature: float = 0.0,
    ) -> LLMResponse:
        start_time = time.time()

        # Fast path: If no API key or circuit breaker is OPEN, instantly use deterministic fallback
        if not self.api_key:
            from app.ai.providers.mock_provider import MockLLMProvider

            return MockLLMProvider(model=self.model).generate(messages, tools, temperature)

        if not gemini_circuit_breaker.can_execute():
            print(
                "[GeminiProvider] Circuit breaker is OPEN. Fast-failing directly to deterministic analysis engine."
            )
            from app.ai.providers.mock_provider import MockLLMProvider

            fallback_res = MockLLMProvider(model=self.model).generate(messages, tools, temperature)
            fallback_res.latency_ms = (time.time() - start_time) * 1000
            return fallback_res

        # Prepare Gemini payload
        system_instructions = []
        contents = []

        for msg in messages:
            if msg.role.lower() == "system":
                system_instructions.append({"text": msg.content})
            elif msg.role.lower() in ["assistant", "model"]:
                contents.append({"role": "model", "parts": [{"text": msg.content}]})
            else:
                contents.append({"role": "user", "parts": [{"text": msg.content}]})

        # Ensure there is at least one content part
        if not contents and system_instructions:
            contents.append({"role": "user", "parts": system_instructions})
            system_instructions = []

        payload: Dict[str, Any] = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": 2048,
            },
        }

        if system_instructions:
            payload["systemInstruction"] = {"parts": system_instructions}

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,
        }

        # Candidate models to try (prioritize fast low-latency models)
        clean_target = (
            self.model[7:] if self.model and self.model.startswith("models/") else self.model
        )
        candidate_models = ["gemini-flash-lite-latest", clean_target, "gemini-flash-latest"]
        unique_models = []
        for m in candidate_models:
            if m and m not in unique_models:
                unique_models.append(m)

        last_error = None
        for m_name in unique_models[:2]:  # Test at most 2 candidate models
            api_url = (
                f"https://generativelanguage.googleapis.com/v1beta/models/{m_name}:generateContent"
            )
            try:
                with httpx.Client(timeout=20.0) as client:
                    resp = client.post(
                        api_url, headers=headers, json=payload, params={"key": self.api_key}
                    )
                    # For auth / permission errors, stop retrying models immediately
                    if resp.status_code in [400, 401, 403]:
                        resp.raise_for_status()

                    resp.raise_for_status()
                    data = resp.json()

                # Parse Gemini response
                candidates = data.get("candidates", [])
                content_text = ""
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    content_text = "".join(p.get("text", "") for p in parts)

                usage = data.get("usageMetadata", {})
                prompt_tokens = usage.get("promptTokenCount", 0)
                completion_tokens = usage.get("candidatesTokenCount", 0)
                total_tokens = usage.get("totalTokenCount", prompt_tokens + completion_tokens)
                latency_ms = (time.time() - start_time) * 1000

                estimated_cost = (prompt_tokens * 0.000000075) + (completion_tokens * 0.00000030)

                # Record success to close circuit breaker
                gemini_circuit_breaker.record_success()

                return LLMResponse(
                    content=content_text.strip(),
                    tool_calls=[],
                    model=m_name,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                    estimated_cost_usd=round(estimated_cost, 7),
                    latency_ms=round(latency_ms, 2),
                )
            except httpx.HTTPStatusError as e:
                last_error = e
                if e.response.status_code in [400, 401, 403]:
                    # Bad credentials - break immediately to trigger fallback and record failure
                    break
            except Exception as e:
                last_error = e
                continue

        # Record failure on circuit breaker
        gemini_circuit_breaker.record_failure(last_error)

        # Fallback gracefully to MockLLMProvider
        print(
            f"[GeminiProvider Warning] Gemini API call failed ({last_error}). Gracefully falling back to deterministic analysis engine."
        )
        from app.ai.providers.mock_provider import MockLLMProvider

        fallback_res = MockLLMProvider(model=self.model).generate(messages, tools, temperature)
        fallback_res.latency_ms = (time.time() - start_time) * 1000
        return fallback_res
