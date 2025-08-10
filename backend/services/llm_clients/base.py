from abc import ABC, abstractmethod
from typing import Dict, Any

class LLMClientInterface(ABC):
    """LLMクライアントの共通インターフェース"""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        **kwargs
    ) -> Dict[str, Any]:
        """LLMから応答を生成"""
        pass

    @abstractmethod
    async def validate_response(self, response: Dict[str, Any]) -> bool:
        """応答の妥当性を検証"""
        pass