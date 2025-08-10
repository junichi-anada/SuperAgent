import re
from typing import List, Optional, Dict

class ImageRequestDetector:
    """ユーザーのメッセージから画像要求を検出するサービス"""
    
    def __init__(self):
        # 画像要求を示すトリガーワードのパターン
        self.trigger_patterns = [
            r"写真.*(?:ほしい|欲しい|ください|下さい)",
            r"画像.*(?:ほしい|欲しい|ください|下さい)",
            r"(?:写真|画像).*(?:見せて|みせて|送って|おくって)",
            r"(?:写真|画像).*(?:見たい|みたい)",
            r"(?:写真|画像).*(?:ある？|ありますか|ありませんか)",
            r"(?:その時|そのとき|それ)の.*(?:写真|画像)",
            r"(?:別角度|べつかくど|違う角度).*(?:写真|画像)",
            r"(?:全身|ぜんしん).*(?:写真|画像)",
            r"(?:アップ|クローズアップ).*(?:写真|画像)",
        ]
        
        # コンパイル済みの正規表現パターン
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.trigger_patterns]
    
    def detect_image_request(self, user_message: str) -> bool:
        """
        ユーザーメッセージから画像要求を検出
        
        Args:
            user_message: ユーザーのメッセージ
            
        Returns:
            画像要求が検出された場合True
        """
        # 各パターンをチェック
        for pattern in self.compiled_patterns:
            if pattern.search(user_message):
                return True
        
        return False
    
    def extract_image_context(self, user_message: str) -> Optional[Dict[str, str]]:
        """
        画像要求から具体的なコンテキストを抽出し、日本語と英語のキーワード辞書を返す
        
        Args:
            user_message: ユーザーのメッセージ
            
        Returns:
            抽出されたキーワード辞書（例: {"公園": "park", "全身": "full body"}）
        """
        context_patterns = [
            # パターン, 日本語キーワード, 英語キーワード
            (r"(別角度|べつかくど|違う角度)", "別角度", "different angle"),
            (r"(全身|ぜんしん)", "全身", "full body"),
            (r"(アップ|クローズアップ|顔)", "クローズアップ", "close-up"),
            (r"(その時|そのとき|それ)の", "文脈依存", "context-dependent"),
            (r"(昨日|きのう)", "昨日", "yesterday"),
            (r"(今日|きょう)", "今日", "today"),
            (r"(公園|こうえん)", "公園", "park"),
            (r"(海|うみ|ビーチ)", "海・ビーチ", "beach, ocean"),
            (r"(室内|しつない|部屋|へや)", "室内", "indoor, room"),
            (r"(外|そと|屋外|おくがい)", "屋外", "outdoor"),
            (r"(笑って|わらって)", "笑顔", "smiling"),
            (r"(座って|すわって)", "座る", "sitting"),
        ]
        
        extracted_keywords = {}
        
        for pattern, jp_keyword, en_keyword in context_patterns:
            if re.search(pattern, user_message, re.IGNORECASE):
                extracted_keywords[jp_keyword] = en_keyword
        
        return extracted_keywords if extracted_keywords else None
    
    def get_image_type_hint(self, user_message: str) -> str:
        """
        要求されている画像のタイプを推測
        
        Args:
            user_message: ユーザーのメッセージ
            
        Returns:
            画像タイプのヒント（"portrait", "full_body", "scene"など）
        """
        if re.search(r"(全身|ぜんしん|立って|たって)", user_message, re.IGNORECASE):
            return "full_body"
        elif re.search(r"(顔|かお|アップ|クローズアップ)", user_message, re.IGNORECASE):
            return "closeup"
        elif re.search(r"(別角度|べつかくど|違う角度|横|よこ|後ろ|うしろ)", user_message, re.IGNORECASE):
            return "different_angle"
        elif re.search(r"(その時|そのとき|場面|ばめん|シーン)", user_message, re.IGNORECASE):
            return "scene"
        else:
            return "portrait"  # デフォルト