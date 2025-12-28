from typing import List, Dict, Any
from openai import OpenAI
from app.config import settings
from .base import ChatProvider

class OpenAICompatibleProvider(ChatProvider):
    def __init__(self):
        self.client = OpenAI(base_url=settings.internal_base_url, api_key=settings.internal_api_key)

    def chat(self, messages: List[Dict[str, Any]]) -> str:
        resp = self.client.chat.completions.create(
            model=settings.internal_model,
            messages=messages,
            temperature=0.2,
        )
        return resp.choices[0].message.content or ""
