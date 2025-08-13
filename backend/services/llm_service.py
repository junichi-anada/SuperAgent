from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
import crud
import models
from .prompt_builder import PromptBuilder
from .llm_clients.base import LLMClientInterface
from .error_handler import ErrorHandler
from .image_request_detector import ImageRequestDetector
from .image_prompt_analyzer import ImagePromptAnalyzer
from .image_generation_service import ImageGenerationService
from .r18_content_analyzer import R18ContentAnalyzer, analyze_r18_score
import logging
import asyncio

logger = logging.getLogger(__name__)

class LLMService:
    """LLM統合の中核サービス"""

    def __init__(
        self,
        prompt_builder: PromptBuilder,
        llm_client: LLMClientInterface,
        error_handler: ErrorHandler,
        image_request_detector: Optional[ImageRequestDetector] = None,
        image_prompt_analyzer: Optional[ImagePromptAnalyzer] = None,
        image_generation_service: Optional[ImageGenerationService] = None,
        r18_content_analyzer: Optional[R18ContentAnalyzer] = None,
        r18_mode_chat: bool = False,
    ):
        self.prompt_builder = prompt_builder
        self.llm_client = llm_client
        self.error_handler = error_handler
        
        # 画像生成関連のサービス（オプショナル）
        self.image_request_detector = image_request_detector
        self.image_prompt_analyzer = image_prompt_analyzer
        self.image_generation_service = image_generation_service
        
        # R18関連サービス
        self.r18_content_analyzer = r18_content_analyzer
        
        # R18モード設定
        self.r18_mode_chat = r18_mode_chat

    async def generate_response(
        self,
        db: Session,
        message: str,
        agent: models.Agent,
        chat_id: int,
        user_message_id: int,
        websocket: Optional[Any] = None,  # WebSocketオブジェクトをオプショナルで受け取る
    ) -> Dict[str, Any]:
        """エージェントのパーソナリティを反映した応答を生成"""
        try:
            # 1. エージェント情報とコンテキストを取得
            # Agent is now passed directly
            if not agent:
                raise ValueError("Agent object is required")
                
            # For simplicity, we get the last 5 messages as context.
            db_messages = crud.get_messages(db, chat_id=chat_id, skip=0, limit=5)
            context = [
                {"sender": msg.sender, "content": msg.content}
                for msg in reversed(db_messages)
            ]

            # 2. プロンプトを構築
            prompt = await self.prompt_builder.build(
                agent=agent,
                message=message,
                context=context,
                r18_mode_chat=self.r18_mode_chat
            )

            # 3. LLM APIを呼び出し
            logger.info(f"Calling LLM API for agent {agent.id} with message: {message[:50]}...")
            raw_response = await self.llm_client.generate(prompt)

            # 4. 応答を処理・検証 (簡易版)
            is_valid = await self.llm_client.validate_response(raw_response)
            if not is_valid:
                logger.error(f"Invalid response from LLM for agent {agent.id}")
                raise ValueError("Invalid response from LLM")

            response_content = raw_response["content"]
            
            r18_score = None  # R18スコアを保持する変数を初期化
            # R18スコアの計算と送信
            if self.r18_content_analyzer and websocket:
                try:
                    # ユーザーメッセージとAI応答を結合して分析
                    combined_text = message + " " + response_content
                    r18_score = self.r18_content_analyzer.analyze(combined_text)
                    
                    await websocket.send_json({
                        "type": "status",
                        "status": "r18_score_updated",
                        "message": f"R18スコア: {r18_score}",
                        "r18_score": r18_score
                    })
                    logger.info(f"Sent R18 score to client: {r18_score}")
                except Exception as e:
                    logger.error(f"Failed to send R18 score: {e}")
            image_url = None
            
            # 5. 画像要求の検出と処理
            if self.image_request_detector and self.image_prompt_analyzer and self.image_generation_service:
                try:
                    # 画像要求を検出
                    if self.image_request_detector.detect_image_request(message):
                        logger.info(f"Image request detected in message: {message}")
                        
                        # 画像生成タスクを非同期で開始
                        if websocket:
                            try:
                                status_message = "画像を生成しています..."
                                if r18_score is not None:
                                    status_message += f" (R18スコア: {r18_score})"
                                
                                await websocket.send_json({
                                    "type": "status",
                                    "status": "image_generation_started",
                                    "message": status_message,
                                    "r18_score": r18_score
                                })
                            except Exception as ws_error:
                                logger.warning(f"Failed to send WebSocket status: {ws_error}")
                        
                        image_url = await self._handle_image_generation(
                            db, message, response_content, agent, context, chat_id, user_message_id, websocket
                        )
                        
                except Exception as e:
                    logger.error(f"Failed to handle image generation: {e}", exc_info=True)
                    # 画像生成に失敗してもチャットは続行

            # 6. レスポンスを返す
            logger.info(f"Successfully generated response for agent {agent.id}")
            return {
                "content": response_content,
                "image_url": image_url,
                "metadata": {
                    "model": raw_response.get("model"),
                    "usage": raw_response.get("usage"),
                    "image_generated": image_url is not None
                }
            }
        except Exception as e:
            logger.error(f"Error in generate_response for agent {agent.id}: {str(e)}", exc_info=True)
            return self.error_handler.handle(e, agent_id=agent.id)

    async def _handle_image_generation(
        self,
        db: Session,
        user_message: str,
        agent_response: str,
        agent: models.Agent,
        context: List[Dict[str, str]],
        chat_id: int,
        user_message_id: int,
        websocket: Optional[Any] = None,
    ) -> Optional[str]:
        """画像生成を処理し、URLを返す"""
        try:
            # 画像のコンテキストとタイプを抽出
            extracted_keywords = self.image_request_detector.extract_image_context(user_message)
            image_type = self.image_request_detector.get_image_type_hint(user_message)
            
            logger.info(f"Extracted keywords: {extracted_keywords}, Image type: {image_type}")
            
            # プロンプトを分析・構築
            prompt_data = await self.image_prompt_analyzer.analyze_and_build_prompt(
                user_message=user_message,
                agent_response=agent_response,
                agent=agent,
                context=context,
                image_type=image_type,
                extracted_keywords=extracted_keywords,
                is_user_request=True
            )
            
            # 画像を生成
            logger.info(f"Generating image with prompt: {prompt_data['prompt']}")
            
            image_url, _ = await self.image_generation_service.generate_image_in_chat(
                db=db,
                agent=agent,
                prompt=prompt_data["prompt"],
                user_message=user_message,
                keywords=extracted_keywords,
                chat_id=chat_id,
                message_id=user_message_id,
                force_regenerate=True,
                websocket=websocket
            )
            
            logger.info(f"Image generated and saved: {image_url}")
            return image_url
                
        except Exception as e:
            logger.error(f"Error in image generation: {e}", exc_info=True)
            return None