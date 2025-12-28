from abc import ABC, abstractmethod
from typing import List, Dict, Any

class ChatProvider(ABC):
    @abstractmethod
    def chat(self, messages: List[Dict[str, Any]]) -> str:
        ...
