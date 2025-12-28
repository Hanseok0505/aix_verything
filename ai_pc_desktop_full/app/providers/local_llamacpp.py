import os
from typing import List, Dict, Any
from llama_cpp import Llama
from app.config import settings
from .base import ChatProvider

class LocalLlamaCppProvider(ChatProvider):
    def __init__(self):
        if not os.path.exists(settings.local_gguf_path):
            raise FileNotFoundError(
                f"GGUF 모델 파일을 찾을 수 없습니다: {settings.local_gguf_path}\n"
                "모델을 다운로드하거나 경로를 확인해주세요."
            )
        self.llm = Llama(
            model_path=settings.local_gguf_path,
            n_ctx=settings.local_ctx,
            n_threads=settings.local_threads,
            verbose=False
        )

    def chat(self, messages: List[Dict[str, Any]]) -> str:
        """메시지 리스트를 받아 LLM 응답 생성"""
        # llama.cpp는 특정 포맷을 선호하므로, 시스템 메시지와 사용자 메시지를 결합
        prompt_parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                prompt_parts.append(f"System: {content}\n")
            elif role == "user":
                prompt_parts.append(f"User: {content}\n")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}\n")
        
        prompt_parts.append("Assistant: ")
        prompt = "".join(prompt_parts)
        
        # 생성 파라미터
        response = self.llm(
            prompt,
            max_tokens=512,
            temperature=0.2,
            stop=["User:", "System:", "\n\n\n"],
            echo=False
        )
        
        return response["choices"][0]["text"].strip()

