from typing import List, Dict, Any
from .base import ChatProvider

class LocalStubProvider(ChatProvider):
    def chat(self, messages: List[Dict[str, Any]]) -> str:
        return (
            "Local LLM is not bundled in this build. "
            "Set AI_PC_MODE=internal to use your internal proxy, "
            "or install llama-cpp-python and implement local provider."
        )
