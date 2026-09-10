import time
from typing import Any, Dict, List, Optional

import httpx

from app.ai.schemas.llm_schemas import LLMMessage, LLMResponse


class AnthropicProvider:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.api_key = api_key
        self.model = model or "claude-3-5-sonnet-20241022"
        self.base_url = base_url or "https://api.anthropic.com/v1"

    def generate(
        self,
        messages: List[LLMMessage],
        tools: List[Dict[str, Any]] = None,
        temperature: float = 0.0,
    ) -> LLMResponse:
        if not self.api_key or self.api_key == "mock-key":
            from app.ai.providers.mock_provider import MockLLMProvider

            return MockLLMProvider(model=self.model).generate(messages, tools, temperature)

        start_time = time.time()
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        # Separate system message if present
        system_content = ""
        anthropic_msgs = []
        for msg in messages:
            if msg.role == "system":
                system_content += msg.content + "\n"
            else:
                anthropic_msgs.append({"role": msg.role, "content": msg.content})

        if not anthropic_msgs:
            anthropic_msgs = [{"role": "user", "content": system_content}]
            system_content = ""

        payload: Dict[str, Any] = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": anthropic_msgs,
            "temperature": temperature,
        }
        if system_content.strip():
            payload["system"] = system_content.strip()

        endpoint = f"{self.base_url.rstrip('/')}/messages"

        with httpx.Client(timeout=35.0) as client:
            resp = client.post(endpoint, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        content_text = ""
        for block in data.get("content", []):
            if block.get("type") == "text":
                content_text += block.get("text", "")

        usage = data.get("usage", {})
        latency_ms = (time.time() - start_time) * 1000

        return LLMResponse(
            content=content_text,
            tool_calls=[],
            model=self.model,
            prompt_tokens=usage.get("input_tokens", 0),
            completion_tokens=usage.get("output_tokens", 0),
            total_tokens=usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
            estimated_cost_usd=(usage.get("input_tokens", 0) * 0.000003)
            + (usage.get("output_tokens", 0) * 0.000015),
            latency_ms=latency_ms,
        )
