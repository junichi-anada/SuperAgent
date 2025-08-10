import pytest
from services.image_request_detector import ImageRequestDetector


class TestImageRequestDetector:
    """ImageRequestDetectorのテストクラス"""
    
    def setup_method(self):
        """各テストメソッドの前に実行される"""
        self.detector = ImageRequestDetector()
    
    def test_detect_image_request_basic_patterns(self):
        """基本的な画像要求パターンの検出テスト"""
        # 検出されるべきパターン
        positive_cases = [
            "写真がほしい",
            "画像が欲しい",
            "写真をください",
            "画像を下さい",
            "写真見せて",
            "画像みせて",
            "写真送って",
            "画像をおくって",
            "写真が見たい",
            "画像みたい",
            "写真ある？",
            "画像ありますか",
            "写真ありませんか",
        ]
        
        for message in positive_cases:
            assert self.detector.detect_image_request(message), f"Failed to detect: {message}"
    
    def test_detect_image_request_complex_patterns(self):
        """複雑な画像要求パターンの検出テスト"""
        positive_cases = [
            "その時の写真がほしい",
            "そのときの画像を見せて",
            "昨日の写真送って",
            "別角度から見た写真がほしい",
            "べつかくどの画像ください",
            "全身の写真が見たい",
            "ぜんしんの画像ある？",
            "アップの写真を送って",
            "クローズアップの画像がほしい",
        ]
        
        for message in positive_cases:
            assert self.detector.detect_image_request(message), f"Failed to detect: {message}"
    
    def test_not_detect_non_image_requests(self):
        """画像要求でないメッセージの非検出テスト"""
        negative_cases = [
            "今日の天気はどう？",
            "写真について話そう",
            "画像処理の方法を教えて",
            "カメラの使い方を知りたい",
            "昨日は楽しかった",
            "",
        ]
        
        for message in negative_cases:
            assert not self.detector.detect_image_request(message), f"Incorrectly detected: {message}"
    
    def test_extract_image_context(self):
        """画像コンテキストの抽出テスト"""
        test_cases = [
            ("別角度から見た写真がほしい", "別角度"),
            ("全身の画像を見せて", "全身"),
            ("顔のアップの写真ください", "クローズアップ"),
            ("その時の写真が見たい", "文脈依存"),
            ("昨日の公園での写真ある？", "昨日, 公園"),
            ("今日の海の写真を送って", "今日, 海・ビーチ"),
            ("室内での写真がほしい", "室内"),
            ("外で撮った写真見せて", "屋外"),
        ]
        
        for message, expected_context in test_cases:
            context = self.detector.extract_image_context(message)
            assert context is not None, f"No context extracted from: {message}"
            # 期待されるコンテキストの各要素が含まれているかチェック
            for expected_part in expected_context.split(", "):
                assert expected_part in context, f"Expected '{expected_part}' in context for: {message}, but got: {context}"
    
    def test_extract_image_context_no_context(self):
        """コンテキストが抽出されない場合のテスト"""
        messages = [
            "写真がほしい",
            "画像を見せて",
            "",
        ]
        
        for message in messages:
            context = self.detector.extract_image_context(message)
            assert context is None, f"Unexpected context extracted from: {message}"
    
    def test_get_image_type_hint(self):
        """画像タイプヒントの取得テスト"""
        test_cases = [
            ("全身の写真がほしい", "full_body"),
            ("ぜんしんで立っている画像", "full_body"),
            ("顔のアップを見せて", "closeup"),
            ("クローズアップの写真", "closeup"),
            ("別角度から見た画像", "different_angle"),
            ("横から撮った写真", "different_angle"),
            ("後ろ姿の写真", "different_angle"),
            ("その時の場面の写真", "scene"),
            ("そのときのシーンを見せて", "scene"),
            ("普通の写真がほしい", "portrait"),  # デフォルト
            ("", "portrait"),  # デフォルト
        ]
        
        for message, expected_type in test_cases:
            image_type = self.detector.get_image_type_hint(message)
            assert image_type == expected_type, f"Expected type '{expected_type}' for: {message}, but got: {image_type}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])