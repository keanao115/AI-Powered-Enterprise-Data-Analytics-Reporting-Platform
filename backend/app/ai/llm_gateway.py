from typing import Any, Dict, List, Optional
from app.core.config import settings
from app.ai.schemas.llm_schemas import LLMMessage, LLMResponse
from app.ai.providers.mock_provider import MockLLMProvider
from app.ai.providers.openai_provider import OpenAIProvider
from app.ai.providers.gemini_provider import GeminiProvider


class LLMGateway:
    def __init__(self, provider_name: Optional[str] = None, model: Optional[str] = None):
        self.provider_name = (provider_name or settings.LLM_PROVIDER).lower()
        self.model = model or settings.LLM_MODEL

    def get_provider(self):
        if self.provider_name in ["gemini", "google"]:
            return GeminiProvider(api_key=settings.GEMINI_API_KEY, model=self.model)
        elif self.provider_name == "openai":
            return OpenAIProvider(model=self.model)
        else:
            return MockLLMProvider(model=self.model)

    def generate(
        self,
        messages: List[LLMMessage],
        tools: List[Dict[str, Any]] = None,
        temperature: float = 0.0,
    ) -> LLMResponse:
        provider = self.get_provider()
        return provider.generate(messages=messages, tools=tools, temperature=temperature)


llm_gateway = LLMGateway()
