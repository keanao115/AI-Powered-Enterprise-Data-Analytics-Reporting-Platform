"""
Universal API Key Pattern Detector.
Automatically detects target AI provider, recommended models, and default base URL from any API key.
"""

from typing import List, Optional

from pydantic import BaseModel


class DetectedProviderInfo(BaseModel):
    provider_id: str
    provider_name: str
    confidence: str  # HIGH, MEDIUM, LOW
    recommended_models: List[str]
    default_model: str
    default_base_url: Optional[str] = None
    key_format_hint: str
    description: str


KNOWN_PROVIDERS = [
    {
        "id": "gemini",
        "name": "Google Gemini",
        "default_model": "gemini-flash-latest",
        "models": [
            "gemini-flash-latest",
            "gemini-flash-lite-latest",
            "gemini-1.5-flash",
            "gemini-1.5-pro",
        ],
        "base_url": None,
        "description": "Google multimodal AI with ultra-fast inference and high reasoning accuracy.",
    },
    {
        "id": "openai",
        "name": "OpenAI",
        "default_model": "gpt-4o-mini",
        "models": [
            "gpt-4o-mini",
            "gpt-4o",
            "gpt-3.5-turbo",
            "o1-mini",
        ],
        "base_url": "https://api.openai.com/v1",
        "description": "Industry standard GPT reasoning and Text-to-SQL generation.",
    },
    {
        "id": "deepseek",
        "name": "DeepSeek AI",
        "default_model": "deepseek-chat",
        "models": [
            "deepseek-chat",
            "deepseek-coder",
            "deepseek-reasoner",
        ],
        "base_url": "https://api.deepseek.com/v1",
        "description": "High-efficiency open-weight reasoning model with state-of-the-art coding and math performance.",
    },
    {
        "id": "anthropic",
        "name": "Anthropic Claude",
        "default_model": "claude-3-5-sonnet-20241022",
        "models": [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
        ],
        "base_url": "https://api.anthropic.com/v1",
        "description": "Safety-oriented reasoning models with strong analytical synthesis and data verification.",
    },
    {
        "id": "groq",
        "name": "Groq Cloud (LPU Inference)",
        "default_model": "llama-3.3-70b-versatile",
        "models": [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "deepseek-r1-distill-llama-70b",
        ],
        "base_url": "https://api.groq.com/openai/v1",
        "description": "Extreme speed LPU inference engine for near-instant Text-to-SQL synthesis.",
    },
    {
        "id": "openrouter",
        "name": "OpenRouter (Unified Gateway)",
        "default_model": "openai/gpt-4o-mini",
        "models": [
            "openai/gpt-4o",
            "openai/gpt-4o-mini",
            "anthropic/claude-3.5-sonnet",
            "google/gemini-flash-1.5",
            "deepseek/deepseek-chat",
        ],
        "base_url": "https://openrouter.ai/api/v1",
        "description": "Unified routing layer connecting 200+ global models with a single API key.",
    },
    {
        "id": "mistral",
        "name": "Mistral AI",
        "default_model": "mistral-large-latest",
        "models": [
            "mistral-large-latest",
            "mistral-small-latest",
            "codestral-latest",
        ],
        "base_url": "https://api.mistral.ai/v1",
        "description": "European high-performance open and frontier models.",
    },
    {
        "id": "mock",
        "name": "Deterministic Engine (Offline / Sandbox)",
        "default_model": "deterministic-v1",
        "models": ["deterministic-v1"],
        "base_url": None,
        "description": "Zero external dependencies. Deterministic rule-based analytical engine for offline demos.",
    },
    {
        "id": "custom",
        "name": "Custom OpenAI-Compatible Endpoint",
        "default_model": "custom-model",
        "models": ["custom-model", "llama3", "qwen-2.5-coder", "mistral"],
        "base_url": "http://localhost:11434/v1",
        "description": "Any self-hosted (vLLM, Ollama, LocalAI) or third-party OpenAI-compatible endpoint.",
    },
]


def detect_provider_from_key(key: str) -> DetectedProviderInfo:
    """
    Intelligently analyzes key prefix and format to detect the target provider.
    Falls back gracefully to OpenAI-compatible or Custom provider if uncertain.
    """
    if not key or not key.strip():
        info = next(p for p in KNOWN_PROVIDERS if p["id"] == "gemini")
        return DetectedProviderInfo(
            provider_id=info["id"],
            provider_name=info["name"],
            confidence="LOW",
            recommended_models=info["models"],
            default_model=info["default_model"],
            default_base_url=info["base_url"],
            key_format_hint="Empty Key",
            description=info["description"],
        )

    clean_key = key.strip()

    # 1. Offline / Mock keywords
    if clean_key.lower() in ("mock", "offline", "deterministic", "sandbox", "local"):
        info = next(p for p in KNOWN_PROVIDERS if p["id"] == "mock")
        return DetectedProviderInfo(
            provider_id="mock",
            provider_name=info["name"],
            confidence="HIGH",
            recommended_models=info["models"],
            default_model=info["default_model"],
            default_base_url=None,
            key_format_hint="Offline Deterministic Keyword",
            description=info["description"],
        )

    # 2. Google Gemini patterns
    # Standard AIzaSy Google API key or AQ. Studio/Vertex keys
    if clean_key.startswith("AIzaSy") or clean_key.startswith("AQ.") or clean_key.startswith("AQ-"):
        info = next(p for p in KNOWN_PROVIDERS if p["id"] == "gemini")
        return DetectedProviderInfo(
            provider_id="gemini",
            provider_name=info["name"],
            confidence="HIGH",
            recommended_models=info["models"],
            default_model=info["default_model"],
            default_base_url=None,
            key_format_hint="Recognized Google Gemini Key Signature (AIzaSy / AQ...)",
            description=info["description"],
        )

    # 3. Anthropic Claude pattern (sk-ant-)
    if clean_key.startswith("sk-ant-"):
        info = next(p for p in KNOWN_PROVIDERS if p["id"] == "anthropic")
        return DetectedProviderInfo(
            provider_id="anthropic",
            provider_name=info["name"],
            confidence="HIGH",
            recommended_models=info["models"],
            default_model=info["default_model"],
            default_base_url=info["base_url"],
            key_format_hint="Recognized Anthropic Claude Key Signature (sk-ant-...)",
            description=info["description"],
        )

    # 4. Groq Cloud pattern (gsk_)
    if clean_key.startswith("gsk_"):
        info = next(p for p in KNOWN_PROVIDERS if p["id"] == "groq")
        return DetectedProviderInfo(
            provider_id="groq",
            provider_name=info["name"],
            confidence="HIGH",
            recommended_models=info["models"],
            default_model=info["default_model"],
            default_base_url=info["base_url"],
            key_format_hint="Recognized Groq LPU Key Signature (gsk_...)",
            description=info["description"],
        )

    # 5. OpenRouter pattern (sk-or-)
    if clean_key.startswith("sk-or-"):
        info = next(p for p in KNOWN_PROVIDERS if p["id"] == "openrouter")
        return DetectedProviderInfo(
            provider_id="openrouter",
            provider_name=info["name"],
            confidence="HIGH",
            recommended_models=info["models"],
            default_model=info["default_model"],
            default_base_url=info["base_url"],
            key_format_hint="Recognized OpenRouter Gateway Key Signature (sk-or-...)",
            description=info["description"],
        )

    # 6. DeepSeek pattern (dsk- or deepseek keyword)
    if clean_key.startswith("dsk-") or "deepseek" in clean_key.lower():
        info = next(p for p in KNOWN_PROVIDERS if p["id"] == "deepseek")
        return DetectedProviderInfo(
            provider_id="deepseek",
            provider_name=info["name"],
            confidence="HIGH",
            recommended_models=info["models"],
            default_model=info["default_model"],
            default_base_url=info["base_url"],
            key_format_hint="Recognized DeepSeek AI Key Signature (dsk-...)",
            description=info["description"],
        )

    # 7. OpenAI Project / Admin pattern (sk-proj- or sk-admin-)
    if clean_key.startswith("sk-proj-") or clean_key.startswith("sk-admin-"):
        info = next(p for p in KNOWN_PROVIDERS if p["id"] == "openai")
        return DetectedProviderInfo(
            provider_id="openai",
            provider_name=info["name"],
            confidence="HIGH",
            recommended_models=info["models"],
            default_model=info["default_model"],
            default_base_url=info["base_url"],
            key_format_hint="Recognized OpenAI Project Key Signature (sk-proj-...)",
            description=info["description"],
        )

    # 8. Generic sk- prefix (Common for OpenAI and DeepSeek / Mistral)
    if clean_key.startswith("sk-"):
        info = next(p for p in KNOWN_PROVIDERS if p["id"] == "openai")
        return DetectedProviderInfo(
            provider_id="openai",
            provider_name=info["name"],
            confidence="MEDIUM",
            recommended_models=info["models"],
            default_model=info["default_model"],
            default_base_url=info["base_url"],
            key_format_hint="Recognized Standard OpenAI-Compatible Key Signature (sk-...)",
            description=info["description"],
        )

    # 9. Custom / Unknown format -> Default to universal OpenAI-compatible endpoint
    info = next(p for p in KNOWN_PROVIDERS if p["id"] == "custom")
    return DetectedProviderInfo(
        provider_id="custom",
        provider_name=info["name"],
        confidence="LOW",
        recommended_models=info["models"],
        default_model=info["default_model"],
        default_base_url=info["base_url"],
        key_format_hint="Custom / Third-party API Key format",
        description=info["description"],
    )
