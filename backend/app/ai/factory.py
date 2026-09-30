import os
from .base import AIProvider
from .ollama_provider import OllamaProvider
from .openai_provider import OpenAIProvider


def get_provider_info() -> dict[str, str]:
    provider = os.getenv("AI_PROVIDER", "ollama").strip().lower()
    if provider == "ollama":
        return {"provider": provider, "model": os.getenv("OLLAMA_MODEL", "qwen2.5:7b")}
    if provider == "openai":
        return {"provider": provider, "model": os.getenv("OPENAI_MODEL", "gpt-4.1-mini")}
    raise RuntimeError(f"Unsupported AI_PROVIDER '{provider}'. Choose 'ollama' or 'openai'.")


def create_provider() -> AIProvider:
    provider = get_provider_info()["provider"]
    if provider == "ollama":
        return OllamaProvider()
    return OpenAIProvider()