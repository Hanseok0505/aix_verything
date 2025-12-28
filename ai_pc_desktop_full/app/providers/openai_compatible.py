from typing import List, Dict, Any
from openai import OpenAI
from app.config import settings
from .base import ChatProvider

class OpenAICompatibleProvider(ChatProvider):
    def __init__(self):
        # Proxy 사용 여부에 따라 URL과 API 키 선택
        if settings.use_proxy:
            base_url = settings.proxy_url
            api_key = settings.proxy_api_key or settings.internal_api_key
        else:
            base_url = settings.internal_base_url
            api_key = settings.internal_api_key
        
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.use_proxy = settings.use_proxy

    def chat(self, messages: List[Dict[str, Any]]) -> str:
        resp = self.client.chat.completions.create(
            model=settings.internal_model,
            messages=messages,
            temperature=0.2,
        )
        return resp.choices[0].message.content or ""
