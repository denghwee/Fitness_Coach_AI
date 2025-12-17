from abc import ABC, abstractmethod

class BaseLLM(ABC):
    @abstractmethod
    def chat(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
        pass

    def moderate(self, text: str):
        """Optional moderation hook. Return provider moderation result or None if not supported."""
        return None