"""
LLM Factory
- Singleton instance
- Based on config (.env)
- Create LLMs instance for agent
"""

from ..config import Config
from .base import BaseLLM
from .ollama_client import OllamaClient
from .openai_client import OpenAIClient

# Singleton instance
_LLM_INSTANCE: BaseLLM | None = None

def get_llm() -> BaseLLM:
    global _LLM_INSTANCE

    if _LLM_INSTANCE is not None:
        return _LLM_INSTANCE
    
    provider = Config.LLM_PROVIDER.lower()

    if provider == "openai":
        _LLM_INSTANCE = OpenAIClient()
    elif provider == "ollama":
        _LLM_INSTANCE = OllamaClient()
    else:
        raise ValueError(
            f"Unsupported LLM_PROVIDER: {Config.LLM_PROVIDER}. "
            "Supported values: openai, ollama"
        )
    
    return _LLM_INSTANCE