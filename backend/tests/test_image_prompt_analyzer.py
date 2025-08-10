import pytest
from unittest.mock import Mock, AsyncMock, patch
from services.image_prompt_analyzer import ImagePromptAnalyzer
from models import Agent


class TestImagePromptAnalyzer:
    """ImagePromptAnalyzerのテストクラス"""
    
    def setup_method(self):
        """各テストメソッドの前に実行される"""
        self.mock_llm_client = Mock()
        self.analyzer = ImagePromptAnalyzer(self.mock_llm_client)
        
        # テスト用のエージェント
        self.test_agent = Agent(
            id=1,
            name="テストエージェント",
            gender="female",
            ethnicity="Japanese",
            age=25,
            hair_style="long straight hair",
            hair_color="black",
            eye_color="brown",
            body_type="slim",
            clothing="casual dress",
            background="modern office"
        )
    
    def test_build_base_appearance(self):
        """基本的な外見属性の構築テスト"""
        result = self.analyzer._build_base_appearance(self.test_agent)
        
        expected_parts = [
            "female",
            "Japanese",
            "25 years old",
            "long straight hair",
            "black hair",
            "brown eyes",
            "slim"
        ]
        
        for part in expected_parts:
            assert part in result, f"Expected '{part}' in base appearance"
    
    def test_build_base_appearance_partial_data(self):
        """部分的なデータでの外見属性構築テスト"""
        partial_agent = Agent(
            id=2,
            name="部分エージェント",
            gender="male",
            age=30
        )
        
        result = self.analyzer._build_base_appearance(partial_agent)
        assert "male" in result
        assert "30 years old" in result
    
    @pytest.mark.asyncio
    async def test_extract_additional_details(self):
        """追加詳細の抽出テスト"""
        user_message = "昨日公園で撮った写真が見たい"
        agent_response = "昨日は楽しかったですね。公園でベンチに座って本を読んでいました。"
        context = [
            {"sender": "user", "content": "どこに行ったの？"},
            {"sender": "ai", "content": "公園に行きました"},
        ]
        
        details = await self.analyzer._extract_additional_details(
            user_message, agent_response, context, {"昨日": "yesterday", "公園": "park"}
        )
        
        assert details.get("scene") == "park"
        assert details.get("activity") == "sitting"
    
    def test_determine_background_with_context(self):
        """コンテキストを使った背景決定テスト"""
        result = self.analyzer._determine_background(
            scene="",
            agent_background="office",
            extracted_keywords={"公園": "park"}
        )
        
        assert result == "(park:1.3)"
    
    def test_determine_background_with_scene(self):
        """シーンを使った背景決定テスト"""
        result = self.analyzer._determine_background(
            scene="beach",
            agent_background="office",
            extracted_keywords=None
        )
        
        assert "beach" in result
        assert "ocean waves" in result
    
    def test_determine_background_default(self):
        """デフォルトの背景決定テスト"""
        result = self.analyzer._determine_background(
            scene="",
            agent_background=None,
            extracted_keywords=None
        )
        
        assert "professional photography studio" in result
    
    def test_construct_final_prompt_with_keywords(self):
        """キーワード付きの最終プロンプト構築テスト"""
        base_appearance = "female, Japanese, 25 years old"
        style = "portrait photography"
        background = "(park:1.3)"
        additional_details = {}
        
        result = self.analyzer._construct_final_prompt(
            base_appearance,
            style,
            background,
            additional_details,
            self.test_agent,
            is_user_request=True,
            extracted_keywords={"公園": "park", "笑顔": "smiling"}
        )
        
        # 必須要素の確認
        assert "(selfie:1.3)" in result
        assert "R3alisticF" in result
        assert "portrait photography" in result
        assert "female, Japanese, 25 years old" in result
        assert "wearing casual dress" in result
        assert "(smiling:1.3)" in result
        assert "(park:1.3)" in result
        assert "High Detail" in result
        assert "photorealistic" in result
    
    def test_build_fallback_prompt(self):
        """フォールバックプロンプトの生成テスト"""
        result = self.analyzer._build_fallback_prompt(self.test_agent)
        
        assert "R3alisticF" in result
        assert "female" in result
        assert "Japanese" in result
        assert "25 years old" in result
        assert "professional photography" in result
    
    def test_generate_negative_prompt(self):
        """ネガティブプロンプトの生成テスト"""
        result = self.analyzer._generate_negative_prompt()
        
        # 主要なネガティブ要素の確認
        negative_elements = [
            "worst quality",
            "low quality",
            "blurry",
            "bad anatomy",
            "deformed",
            "watermark",
            "cartoon",
            "anime"
        ]
        
        for element in negative_elements:
            assert element in result, f"Expected '{element}' in negative prompt"
    
    @pytest.mark.asyncio
    async def test_analyze_and_build_prompt_success(self):
        """プロンプト分析・構築の成功テスト"""
        user_message = "別角度から見た全身の写真がほしい"
        agent_response = "どんな角度がいいですか？"
        context = []
        
        result = await self.analyzer.analyze_and_build_prompt(
            user_message=user_message,
            agent_response=agent_response,
            agent=self.test_agent,
            context=context,
            image_type="full_body",
            extracted_keywords={"別角度": "different angle", "全身": "full body"},
            is_user_request=True
        )
        
        assert "prompt" in result
        assert "negative_prompt" in result
        assert "metadata" in result
        
        # 新しいルールに基づいたプロンプトの確認
        assert "(selfie:1.3)" in result["prompt"]
        assert "full body shot" in result["prompt"]
        assert "(different angle:1.3)" not in result["prompt"] # 背景ではないので含まれない
        assert result["metadata"]["image_type"] == "full_body"
        assert result["metadata"]["extracted_keywords"] == {"別角度": "different angle", "全身": "full body"}
    
    @pytest.mark.asyncio
    async def test_analyze_and_build_prompt_error_handling(self):
        """エラー時のフォールバック処理テスト"""
        # エラーを発生させる設定
        with patch.object(self.analyzer, '_build_base_appearance', side_effect=Exception("Test error")):
            result = await self.analyzer.analyze_and_build_prompt(
                user_message="写真がほしい",
                agent_response="はい",
                agent=self.test_agent,
                context=[],
                image_type="portrait"
            )
        
        # フォールバックプロンプトが返されることを確認
        assert "prompt" in result
        assert "negative_prompt" in result
        assert "metadata" in result
        assert "error" in result["metadata"]
        assert "Test error" in result["metadata"]["error"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])