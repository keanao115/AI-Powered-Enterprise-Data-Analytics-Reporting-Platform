import time
from typing import Any, Dict, List, Optional

import httpx

from app.ai.schemas.llm_schemas import LLMMessage, LLMResponse
from app.core.config import settings


class OpenAIProvider:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.LLM_MODEL
        self.base_url = base_url

    def generate(
        self,
        messages: List[LLMMessage],
        tools: List[Dict[str, Any]] = None,
        temperature: float = 0.0,
    ) -> LLMResponse:
        if not self.api_key or self.api_key == "mock-key":
            # Fallback gracefully to mock provider if API key not provided
            from app.ai.providers.mock_provider import MockLLMProvider

            return MockLLMProvider(model=self.model).generate(messages, tools, temperature)

        start_time = time.time()
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        formatted_msgs = [{"role": msg.role, "content": msg.content} for msg in messages]
        payload = {
            "model": self.model,
            "messages": formatted_msgs,
            "temperature": temperature,
        }
        if tools:
            payload["tools"] = tools

        endpoint = (
            f"{self.base_url.rstrip('/')}/chat/completions"
            if self.base_url
            else "https://api.openai.com/v1/chat/completions"
        )

        with httpx.Client(timeout=30.0) as client:
            resp = client.post(endpoint, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        choice = data["choices"][0]["message"]
        usage = data.get("usage", {})
        latency_ms = (time.time() - start_time) * 1000

        return LLMResponse(
            content=choice.get("content") or "",
            tool_calls=choice.get("tool_calls", []),
            model=self.model,
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            total_tokens=usage.get("total_tokens", 0),
            estimated_cost_usd=(usage.get("prompt_tokens", 0) * 0.000005)
            + (usage.get("completion_tokens", 0) * 0.000015),
            latency_ms=latency_ms,
        )
