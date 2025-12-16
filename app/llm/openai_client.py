from openai import OpenAI
from .base import BaseLLM
from ..config import Config

class OpenAIClient(BaseLLM):
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPEN_API_KEY)
        self.model = Config.OPENAI_MODEL

    def chat(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature or Config.DEFAULT_TEMPERATURE
        )
        return response.choices[0].message.content