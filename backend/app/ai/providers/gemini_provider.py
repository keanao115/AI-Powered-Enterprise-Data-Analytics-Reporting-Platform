import os
import time
from typing import Any, Dict, List, Optional
import httpx
from app.core.config import settings
from app.ai.schemas.llm_schemas import LLMMessage, LLMResponse


class GeminiProvider:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = api_key or settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        self.model = model or getattr(settings, "GEMINI_MODEL", "gemini-3.6-flash") or "gemini-3.6-flash"

    def generate(
        self,
        messages: List[LLMMessage],
        tools: List[Dict[str, Any]] = None,
        temperature: float = 0.0,
    ) -> LLMResponse:
        start_time = time.time()

        if not self.api_key:
            # Fallback gracefully to mock provider if API key not provided
            from app.ai.providers.mock_provider import MockLLMProvider
            return MockLLMProvider(model=self.model).generate(messages, tools, temperature)

        # Prepare Gemini payload
        system_instructions = []
        contents = []

        for msg in messages:
            if msg.role.lower() == "system":
                system_instructions.append({"text": msg.content})
            elif msg.role.lower() in ["assistant", "model"]:
                contents.append({
                    "role": "model",
                    "parts": [{"text": msg.content}]
                })
            else:
                contents.append({
                    "role": "user",
                    "parts": [{"text": msg.content}]
                })

        # Ensure there is at least one content part
        if not contents and system_instructions:
            contents.append({
                "role": "user",
                "parts": system_instructions
            })
            system_instructions = []

        payload: Dict[str, Any] = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": 2048,
            }
        }

        if system_instructions:
            payload["systemInstruction"] = {
                "parts": system_instructions
            }

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,
        }

        # Candidate models to try in order of priority
        candidate_models = [
            "gemini-3.1-flash-lite-preview",
            "gemini-3-flash-preview",
            "gemini-3.1-flash-lite",
            "gemini-3.7-flash",
            "gemini-flash-latest",
        ]
        if self.model and self.model not in candidate_models:
            clean_m = self.model[7:] if self.model.startswith("models/") else self.model
            candidate_models.insert(0, clean_m)

        unique_models = []
        for m in candidate_models:
            if m not in unique_models:
                unique_models.append(m)

        last_error = None
        for m_name in unique_models:
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{m_name}:generateContent"
            try:
                with httpx.Client(timeout=8.0) as client:
                    resp = client.post(
                        api_url,
                        headers=headers,
                        json=payload,
                        params={"key": self.api_key}
                    )
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
            except Exception as e:
                last_error = e
                continue

        # If all Gemini models fail (e.g. offline or quota), fallback gracefully to MockLLMProvider
        print(f"[GeminiProvider Warning] All Gemini API models failed ({last_error}). Falling back to deterministic analysis engine.")
        from app.ai.providers.mock_provider import MockLLMProvider
        fallback_res = MockLLMProvider(model=self.model).generate(messages, tools, temperature)
        fallback_res.latency_ms = (time.time() - start_time) * 1000
        return fallback_res
