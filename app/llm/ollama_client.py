import requests
from app.llm.base import BaseLLM
from ..config import Config

class OllamaClient(BaseLLM):
    def __init__(self):
        self.model = Config.OLLAMA_MODEL
        self.url = Config.OLLAMA_BASE_URL

    def chat(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": False,
            "options": {
                "temperature": temperature or Config.DEFAULT_TEMPERATURE
            }
        }

        response = requests.post(self.url, json=payload, timeout=120)
        response.raise_for_status()
        return response.json()["message"]["content"]