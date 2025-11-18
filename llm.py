# healthsync_ai/llm.py
from typing import List, Dict
from openai import OpenAI

from config import settings


class LLMClient:
    """
    Thin wrapper around OpenRouter's chat completions.
    Easy to swap out model/provider later.
    """

    def __init__(self, model: str | None = None):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.openrouter_api_key,
        )
        self.model = model or settings.model_name

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.2) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
        )
        return resp.choices[0].message.content
