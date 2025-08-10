import json
import re
from typing import Dict, Any, Optional
from .prompt_builder import PromptBuilder
from .llm_clients.base import LLMClientInterface
from .error_handler import ErrorHandler
import logging

logger = logging.getLogger(__name__)

class FeedbackService:
    """ユーザーからのフィードバックを処理するサービス"""

    def __init__(
        self,
        prompt_builder: PromptBuilder,
        llm_client: LLMClientInterface,
        error_handler: ErrorHandler,
    ):
        self.prompt_builder = prompt_builder
        self.llm_client = llm_client
        self.error_handler = error_handler

    async def extract_second_person(self, message: str) -> Optional[str]:
        """ユーザーメッセージから二人称を抽出する"""
        try:
            prompt = await self.prompt_builder.build(
                message=message,
                template_name="extract_second_person.j2"
            )
            
            raw_response = await self.llm_client.generate(prompt)
            response_content = raw_response.get("content", "")

            # 正規表現でJSONブロックを抽出する、より堅牢な方法
            json_match = re.search(r"```json\s*(\{.*?\})\s*```", response_content, re.DOTALL)
            
            json_str = None
            if json_match:
                json_str = json_match.group(1)
            else:
                # フォールバックとして、波括弧で囲まれた最初の有効なJSONオブジェクトを探す
                brace_match = re.search(r"(\{.*?\})", response_content, re.DOTALL)
                if brace_match:
                    json_str = brace_match.group(1)

            if not json_str:
                logger.error("応答からJSONオブジェクトが見つかりませんでした。")
                return None

            data = json.loads(json_str)
            
            second_person = data.get("second_person")
            
            if second_person and isinstance(second_person, str) and second_person.strip():
                logger.info(f"二人称の抽出に成功: {second_person}")
                return second_person.strip()
            else:
                logger.info("メッセージに二人称の指定は含まれていませんでした。")
                return None

        except json.JSONDecodeError as e:
            logger.error(f"LLMからの応答のJSONパースに失敗しました: {e}")
            logger.error(f"解析しようとした文字列: {json_str}")
            return None
        except Exception as e:
            logger.error(f"二人称の抽出中に予期せぬエラーが発生しました: {e}", exc_info=True)
            return None