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
__LLM_INSTANCE = BaseLLM | None = None

def get_llm() -> BaseLLM:
    global __LLM_INSTANCE

    if __LLM_INSTANCE is not None:
        return __LLM_INSTANCE
    
    provider = Config.LLM_PROVIDER.lower()

    if provider == "openai":
        __LLM_INSTANCE = OpenAIClient()
    elif provider == "ollama":
        __LLM_INSTANCE = OllamaClient()
    else:
        raise ValueError(
            f"Unsupported LLM_PROVIDER: {Config.LLM_PROVIDER}. "
            "Supported values: openai, ollama"
        )
    
    return __LLM_INSTANCE