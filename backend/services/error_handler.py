import logging
from typing import Dict, Any
from enum import Enum

class ErrorType(Enum):
    API_ERROR = "api_error"
    TIMEOUT = "timeout"
    INVALID_RESPONSE = "invalid_response"
    AGENT_NOT_FOUND = "agent_not_found"
    SYSTEM_ERROR = "system_error"

class ErrorHandler:
    """エラーハンドリングとフォールバック"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.fallback_responses = {
            ErrorType.API_ERROR: "申し訳ございません、AIとの接続に問題が発生しました。",
            ErrorType.TIMEOUT: "申し訳ございません、AIの応答が時間内に得られませんでした。",
            ErrorType.INVALID_RESPONSE: "申し訳ございません、AIから予期せぬ応答がありました。",
            ErrorType.AGENT_NOT_FOUND: "指定されたエージェントが見つかりませんでした。",
            ErrorType.SYSTEM_ERROR: "申し訳ございません、システムエラーが発生しました。",
        }

    def handle(self, error: Exception, agent_id: int = None) -> Dict[str, Any]:
        """エラーを処理してフォールバックレスポンスを返す"""
        error_type = self._classify_error(error)
        
        self.logger.error(
            f"LLM Error - Type: {error_type.value}, "
            f"AgentID: {agent_id}, "
            f"Error: {str(error)}"
        )
        
        fallback_content = self.fallback_responses.get(
            error_type, self.fallback_responses[ErrorType.SYSTEM_ERROR]
        )
        
        return {
            "error": True,
            "error_type": error_type.value,
            "content": fallback_content,
            "fallback": True
        }

    def _classify_error(self, error: Exception) -> ErrorType:
        """エラーを分類"""
        error_message = str(error).lower()
        
        if isinstance(error, TimeoutError):
            return ErrorType.TIMEOUT
        elif "agent not found" in error_message:
            return ErrorType.AGENT_NOT_FOUND
        elif "invalid response" in error_message:
            return ErrorType.INVALID_RESPONSE
        elif "api error" in error_message:
            return ErrorType.API_ERROR
        else:
            return ErrorType.SYSTEM_ERROR