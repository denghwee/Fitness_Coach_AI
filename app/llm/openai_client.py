from openai import OpenAI
from ..config import Config
from .base import BaseLLM

class OpenAIClient(BaseLLM):
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.OPENAI_MODEL

    def chat(self, system_prompt: str, user_prompt: str, temperature=None) -> str:
        response = self.client.responses.create(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            # temperature=temperature or Config.DEFAULT_TEMPERATURE
        )

        return response.output_text

    def moderate(self, text: str):
        """Use OpenAI moderation API if available. Returns moderation result dict or None."""
        try:
            res = self.client.moderations.create(
                model="omni-moderation-latest",
                input=text
            )
            # Normalize to dict-like
            try:
                result = res["results"][0]
            except Exception:
                # fallback attribute access
                result = res.results[0]
            return result
        except Exception:
            return None
