import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from sqlalchemy.orm import Session
from services.llm_service import LLMService
from services.image_request_detector import ImageRequestDetector
from services.image_prompt_analyzer import ImagePromptAnalyzer
from services.image_generation_service import ImageGenerationService
from services.prompt_builder import PromptBuilder
from services.error_handler import ErrorHandler
from models import Agent, Message
import crud


class TestImageGenerationIntegration:
    """画像生成機能の統合テスト"""
    
    def setup_method(self):
        """各テストメソッドの前に実行される"""
        # モックの作成
        self.mock_prompt_builder = Mock(spec=PromptBuilder)
        self.mock_llm_client = Mock()
        self.mock_error_handler = Mock(spec=ErrorHandler)
        self.mock_image_request_detector = Mock(spec=ImageRequestDetector)
        self.mock_image_prompt_analyzer = Mock(spec=ImagePromptAnalyzer)
        self.mock_image_generation_service = Mock(spec=ImageGenerationService)
        
        # LLMServiceのインスタンス作成
        self.llm_service = LLMService(
            prompt_builder=self.mock_prompt_builder,
            llm_client=self.mock_llm_client,
            error_handler=self.mock_error_handler,
            image_request_detector=self.mock_image_request_detector,
            image_prompt_analyzer=self.mock_image_prompt_analyzer,
            image_generation_service=self.mock_image_generation_service
        )
        
        # テスト用のエージェント
        self.test_agent = Agent(
            id=1,
            name="テストエージェント",
            gender="female",
            ethnicity="Japanese",
            age=25,
            hair_style="long straight hair",
            eye_color="brown",
            body_type="slim",
            image_seed=12345
        )
        
        # モックデータベースセッション
        self.mock_db = Mock(spec=Session)
    
    @pytest.mark.asyncio
    async def test_generate_response_with_image_request(self):
        """画像要求を含むメッセージへの応答生成テスト"""
        # セットアップ
        user_message = "あなたの写真がほしい"
        chat_id = 1
        
        # モックの設定
        self.mock_prompt_builder.build = AsyncMock(return_value="test prompt")
        self.mock_llm_client.generate = AsyncMock(return_value={
            "content": "はい、お見せしますね。",
            "model": "test-model"
        })
        self.mock_llm_client.validate_response = AsyncMock(return_value=True)
        
        # 画像要求検出をTrueに設定
        self.mock_image_request_detector.detect_image_request.return_value = True
        self.mock_image_request_detector.extract_image_context.return_value = None
        self.mock_image_request_detector.get_image_type_hint.return_value = "portrait"
        
        # 画像プロンプト分析の設定
        self.mock_image_prompt_analyzer.analyze_and_build_prompt = AsyncMock(return_value={
            "prompt": "test image prompt",
            "negative_prompt": "test negative prompt",
            "metadata": {}
        })
        
        # 画像生成サービスの設定
        mock_client = Mock()
        mock_client.generate_image_async = AsyncMock(return_value=(b"fake_image_data", 12345))
        self.mock_image_generation_service.client = mock_client
        self.mock_image_generation_service.storage_path = Mock()
        self.mock_image_generation_service.storage_path.__str__ = Mock(return_value="static/agent_images")
        
        # crud.get_messagesのモック
        with patch('crud.get_messages', return_value=[]):
            # crud.create_agent_imageのモック
            with patch('crud.create_agent_image') as mock_create_image:
                # ファイル書き込みのモック
                with patch('builtins.open', create=True) as mock_open:
                    mock_file = MagicMock()
                    mock_open.return_value.__enter__.return_value = mock_file
                    
                    # テスト実行
                    result = await self.llm_service.generate_response(
                        db=self.mock_db,
                        message=user_message,
                        agent=self.test_agent,
                        chat_id=chat_id
                    )
        
        # アサーション
        assert result["content"] == "はい、お見せしますね。"
        assert result["image_url"] is not None
        assert "/static/agent_images/" in result["image_url"]
        assert result["metadata"]["image_generated"] is True
        
        # 画像要求検出が呼ばれたことを確認
        self.mock_image_request_detector.detect_image_request.assert_called_once_with(user_message)
        
        # 画像生成が呼ばれたことを確認
        mock_client.generate_image_async.assert_called_once()
        
        # データベースに画像が保存されたことを確認
        mock_create_image.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_response_without_image_request(self):
        """画像要求を含まないメッセージへの応答生成テスト"""
        # セットアップ
        user_message = "今日の天気はどう？"
        chat_id = 1
        
        # モックの設定
        self.mock_prompt_builder.build = AsyncMock(return_value="test prompt")
        self.mock_llm_client.generate = AsyncMock(return_value={
            "content": "今日は晴れていて気持ちいいですよ。",
            "model": "test-model"
        })
        self.mock_llm_client.validate_response = AsyncMock(return_value=True)
        
        # 画像要求検出をFalseに設定
        self.mock_image_request_detector.detect_image_request.return_value = False
        
        # crud.get_messagesのモック
        with patch('crud.get_messages', return_value=[]):
            # テスト実行
            result = await self.llm_service.generate_response(
                db=self.mock_db,
                message=user_message,
                agent=self.test_agent,
                chat_id=chat_id
            )
        
        # アサーション
        assert result["content"] == "今日は晴れていて気持ちいいですよ。"
        assert result["image_url"] is None
        assert result["metadata"]["image_generated"] is False
        
        # 画像要求検出が呼ばれたことを確認
        self.mock_image_request_detector.detect_image_request.assert_called_once_with(user_message)
        
        # 画像生成関連のメソッドが呼ばれていないことを確認
        self.mock_image_prompt_analyzer.analyze_and_build_prompt.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_generate_response_image_generation_error(self):
        """画像生成エラー時の処理テスト"""
        # セットアップ
        user_message = "写真を見せて"
        chat_id = 1
        
        # モックの設定
        self.mock_prompt_builder.build = AsyncMock(return_value="test prompt")
        self.mock_llm_client.generate = AsyncMock(return_value={
            "content": "写真をお見せしますね。",
            "model": "test-model"
        })
        self.mock_llm_client.validate_response = AsyncMock(return_value=True)
        
        # 画像要求検出をTrueに設定
        self.mock_image_request_detector.detect_image_request.return_value = True
        self.mock_image_request_detector.extract_image_context.return_value = None
        self.mock_image_request_detector.get_image_type_hint.return_value = "portrait"
        
        # 画像プロンプト分析でエラーを発生させる
        self.mock_image_prompt_analyzer.analyze_and_build_prompt = AsyncMock(
            side_effect=Exception("Image analysis error")
        )
        
        # crud.get_messagesのモック
        with patch('crud.get_messages', return_value=[]):
            # テスト実行
            result = await self.llm_service.generate_response(
                db=self.mock_db,
                message=user_message,
                agent=self.test_agent,
                chat_id=chat_id
            )
        
        # アサーション
        # エラーが発生してもチャットは継続される
        assert result["content"] == "写真をお見せしますね。"
        assert result["image_url"] is None  # 画像生成に失敗したのでNone
        assert result["metadata"]["image_generated"] is False
    
    @pytest.mark.asyncio
    async def test_handle_image_generation_with_context(self):
        """コンテキストを含む画像生成処理のテスト"""
        # セットアップ
        user_message = "昨日公園で撮った別角度の写真がほしい"
        agent_response = "はい、お見せしますね。"
        context = [
            {"sender": "user", "content": "昨日どこに行った？"},
            {"sender": "ai", "content": "公園に行きました。"},
        ]
        
        # モックの設定
        self.mock_image_request_detector.extract_image_context.return_value = "昨日, 公園, 別角度"
        self.mock_image_request_detector.get_image_type_hint.return_value = "different_angle"
        
        self.mock_image_prompt_analyzer.analyze_and_build_prompt = AsyncMock(return_value={
            "prompt": "different angle shot in park",
            "negative_prompt": "bad quality",
            "metadata": {"context": "昨日, 公園, 別角度"}
        })
        
        # 画像生成サービスの設定
        mock_client = Mock()
        mock_client.generate_image_async = AsyncMock(return_value=(b"fake_image_data", 12345))
        self.mock_image_generation_service.client = mock_client
        self.mock_image_generation_service.storage_path = Mock()
        self.mock_image_generation_service.storage_path.__str__ = Mock(return_value="static/agent_images")
        
        # crud.create_agent_imageのモック
        with patch('crud.create_agent_image') as mock_create_image:
            # ファイル書き込みのモック
            with patch('builtins.open', create=True) as mock_open:
                mock_file = MagicMock()
                mock_open.return_value.__enter__.return_value = mock_file
                
                # テスト実行
                result = await self.llm_service._handle_image_generation(
                    db=self.mock_db,
                    user_message=user_message,
                    agent_response=agent_response,
                    agent=self.test_agent,
                    context=context
                )
        
        # アサーション
        assert result is not None
        assert "/static/agent_images/" in result
        
        # 正しいパラメータで呼ばれたことを確認
        self.mock_image_prompt_analyzer.analyze_and_build_prompt.assert_called_once_with(
            user_message=user_message,
            agent_response=agent_response,
            agent=self.test_agent,
            context=context,
            image_type="different_angle",
            extracted_context="昨日, 公園, 別角度"
        )
        
        # エージェントのシード値が使用されたことを確認
        mock_client.generate_image_async.assert_called_once()
        call_args = mock_client.generate_image_async.call_args
        assert call_args.kwargs["seed"] == 12345


if __name__ == "__main__":
    pytest.main([__file__, "-v"])