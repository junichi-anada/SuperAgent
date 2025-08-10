import re
from typing import Dict, List, Optional, Any
from models import Agent
from services.llm_clients.base import LLMClientInterface
import json
import logging

logger = logging.getLogger(__name__)

class ImagePromptAnalyzer:
    """画像生成のためのプロンプトを分析・構築するサービス"""
    
    def __init__(self, llm_client: LLMClientInterface):
        self.llm_client = llm_client
        
        # 画像生成用のスタイルテンプレート
        self.style_templates = {
            "portrait": "portrait photography, head and shoulders shot, facing camera, studio lighting",
            "full_body": "full body shot, standing pose, full length portrait",
            "closeup": "close-up portrait, detailed face shot, emotional expression",
            "different_angle": "3/4 angle view, dynamic pose, artistic composition",
            "scene": "environmental portrait, candid moment, natural setting"
        }
        
        # シーン別の背景テンプレート
        self.scene_backgrounds = {
            "公園": "in a beautiful park, green trees, natural lighting",
            "海・ビーチ": "at the beach, ocean waves, sunny day",
            "室内": "indoor setting, cozy atmosphere, warm lighting",
            "屋外": "outdoor location, natural environment",
            "昨日": "casual setting, everyday scene",
            "今日": "contemporary setting, modern environment"
        }
    
    async def analyze_and_build_prompt(
        self,
        user_message: str,
        agent_response: str,
        agent: Agent,
        context: List[Dict[str, str]],
        image_type: str = "portrait",
        extracted_keywords: Optional[Dict[str, str]] = None,
        is_user_request: bool = False
    ) -> Dict[str, str]:
        """
        画像生成のためのプロンプトを分析・構築
        
        Args:
            user_message: ユーザーのメッセージ
            agent_response: エージェントの応答
            agent: エージェントオブジェクト
            context: 会話履歴
            image_type: 画像タイプ（portrait, full_body等）
            extracted_keywords: 抽出されたキーワード辞書
            is_user_request: ユーザーからの直接的な画像要求かどうか
            
        Returns:
            プロンプトとネガティブプロンプトを含む辞書
        """
        try:
            # 1. エージェントの基本的な外見属性を取得
            base_appearance = self._build_base_appearance(agent)
            
            # 2. 画像タイプに応じたスタイルを選択
            style = self.style_templates.get(image_type, self.style_templates["portrait"])
            
            # 3. コンテキストから追加の詳細を抽出
            additional_details = await self._extract_additional_details(
                user_message, agent_response, context, extracted_keywords
            )
            
            # 4. 背景やシーンの決定
            background = self._determine_background(
                additional_details.get("scene", ""),
                agent.background,
                extracted_keywords
            )
            
            # 5. プロンプトの構築
            prompt = self._construct_final_prompt(
                base_appearance,
                style,
                background,
                additional_details,
                agent,
                is_user_request=(extracted_keywords is not None),
                extracted_keywords=extracted_keywords
            )
            
            # 6. ネガティブプロンプトの生成
            negative_prompt = self._generate_negative_prompt()
            
            logger.info(f"Generated prompt for image type '{image_type}': {prompt}")
            
            return {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "metadata": {
                    "image_type": image_type,
                    "extracted_keywords": extracted_keywords,
                    "additional_details": additional_details
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze and build prompt: {e}")
            # フォールバックプロンプト
            return {
                "prompt": self._build_fallback_prompt(agent),
                "negative_prompt": self._generate_negative_prompt(),
                "metadata": {"error": str(e)}
            }
    
    def _build_base_appearance(self, agent: Agent) -> str:
        """エージェントの基本的な外見属性を構築"""
        details = []
        
        if agent.gender:
            details.append(agent.gender)
        if agent.ethnicity:
            details.append(agent.ethnicity)
        if agent.age:
            details.append(f"{agent.age} years old")
        if agent.hair_style:
            details.append(agent.hair_style)
        if agent.hair_color:
            details.append(f"{agent.hair_color} hair")
        if agent.eye_color:
            details.append(f"{agent.eye_color} eyes")
        if agent.body_type:
            details.append(agent.body_type)
        
        return ", ".join(filter(None, details))
    
    async def _extract_additional_details(
        self,
        user_message: str,
        agent_response: str,
        context: List[Dict[str, str]],
        extracted_keywords: Optional[Dict[str, str]]
    ) -> Dict[str, Any]:
        """会話から追加の詳細を抽出"""
        # 簡易的な実装：より高度な分析が必要な場合はLLMを使用
        details = {}
        
        # 文脈から場所やアクティビティを推測
        recent_messages = " ".join([msg["content"] for msg in context[-3:]])
        
        # 場所の検出
        location_patterns = [
            (r"公園", "park"),
            (r"海|ビーチ", "beach"),
            (r"カフェ|喫茶店", "cafe"),
            (r"家|部屋|室内", "indoor"),
            (r"街|町|外", "street")
        ]
        
        for pattern, location in location_patterns:
            if re.search(pattern, recent_messages + agent_response, re.IGNORECASE):
                details["scene"] = location
                break
        
        # アクティビティの検出
        activity_patterns = [
            (r"座って|すわって", "sitting"),
            (r"歩いて|あるいて", "walking"),
            (r"笑って|わらって", "smiling"),
            (r"読んで|よんで", "reading"),
            (r"飲んで|のんで", "drinking")
        ]
        
        for pattern, activity in activity_patterns:
            if re.search(pattern, recent_messages + agent_response, re.IGNORECASE):
                details["activity"] = activity
                break
        
        # 時間帯の検出
        time_patterns = [
            (r"朝|あさ|morning", "morning light"),
            (r"昼|ひる|午後|ごご", "afternoon light"),
            (r"夕方|ゆうがた|夕日|ゆうひ", "golden hour"),
            (r"夜|よる|night", "evening atmosphere")
        ]
        
        for pattern, time in time_patterns:
            if re.search(pattern, recent_messages, re.IGNORECASE):
                details["lighting"] = time
                break
        
        return details
    
    def _determine_background(
        self,
        scene: str,
        agent_background: Optional[str],
        extracted_keywords: Optional[Dict[str, str]]
    ) -> str:
        """背景を決定"""
        # 優先順位：抽出されたキーワード > シーン > エージェントのデフォルト背景
        
        if extracted_keywords:
            for jp_keyword, en_keyword in extracted_keywords.items():
                if jp_keyword in self.scene_backgrounds:
                    # ルール1: キーワードを重み付け
                    return f"({en_keyword}:1.3)"
        
        if scene:
            scene_map = {
                "park": "in a beautiful park, green trees, natural lighting",
                "beach": "at the beach, ocean waves, sunny day",
                "cafe": "in a cozy cafe, warm interior, ambient lighting",
                "indoor": "indoor setting, comfortable room, soft lighting",
                "street": "on a city street, urban environment, dynamic atmosphere"
            }
            return scene_map.get(scene, "natural environment")
        
        if agent_background:
            return f"background: {agent_background}"
        
        return "professional photography studio, neutral background"
    
    def _construct_final_prompt(
        self,
        base_appearance: str,
        style: str,
        background: str,
        additional_details: Dict[str, Any],
        agent: Agent,
        is_user_request: bool = False,
        extracted_keywords: Optional[Dict[str, str]] = None
    ) -> str:
        """最終的なプロンプトを構築"""
        prompt_parts = []
        if extracted_keywords is None:
            extracted_keywords = {}

        # ルール2: ユーザー要求の場合、部位指定に応じてプロンプトを変更
        if is_user_request:
            body_part_keywords = {
                "全身": "full body",
                "上半身": "upper body",
                "顔": "close-up face",
            }
            body_part_added = False
            if extracted_keywords:
                for jp_keyword in body_part_keywords:
                    if jp_keyword in extracted_keywords:
                        prompt_parts.append(f"({body_part_keywords[jp_keyword]}:1.3)")
                        body_part_added = True
                        break  # 最初の部位指定のみを優先

            if not body_part_added:
                prompt_parts.append("(upper body:1.3)") # デフォルト

        prompt_parts.append("R3alisticF")
        
        # 基本的な外見
        if base_appearance:
            prompt_parts.append(f"a {style} of a {base_appearance}")
        else:
            prompt_parts.append(f"a {style}")
        
        # 服装
        if agent.clothing:
            prompt_parts.append(f"wearing {agent.clothing}")
        
        # アクティビティ
        activity_keyword_map = {"笑顔": "smiling", "座る": "sitting"}
        activity_added = False
        for jp_keyword, en_keyword in extracted_keywords.items():
            if jp_keyword in activity_keyword_map:
                prompt_parts.append(f"({en_keyword}:1.3)")
                activity_added = True
                break # 複数のアクティビティは一旦考慮しない
        
        if not activity_added and additional_details.get("activity"):
             prompt_parts.append(additional_details["activity"])

        # 背景
        # 重み付けは_determine_backgroundで処理済み
        prompt_parts.append(background)
        
        # 照明
        if additional_details.get("lighting"):
            prompt_parts.append(additional_details["lighting"])
        else:
            prompt_parts.append("perfect lighting")
        
        # 品質修飾子
        prompt_parts.extend([
            "High Detail",
            "Perfect Composition",
            "photorealistic",
            "professional photography",
            "sharp focus",
            "detailed skin texture",
            "natural pose",
            "8k resolution",
            "masterpiece"
        ])
        
        return ", ".join(prompt_parts)
    
    def _build_fallback_prompt(self, agent: Agent) -> str:
        """フォールバックプロンプトを生成"""
        details = []
        
        if agent.gender:
            details.append(agent.gender)
        if agent.ethnicity:
            details.append(agent.ethnicity)
        if agent.age:
            details.append(f"{agent.age} years old")
        
        base = ", ".join(filter(None, details)) if details else "person"
        
        return f"R3alisticF, a portrait of a {base}, professional photography, studio lighting, high quality, detailed, sharp focus, 8k resolution"
    
    def _generate_negative_prompt(self) -> str:
        """ネガティブプロンプトを生成"""
        return "(worst quality:2), (low quality:2), (normal quality:2), (jpeg artifacts), (blurry), (duplicate), (morbid), (mutilated), (out of frame), (extra limbs), (bad anatomy), (disfigured), (deformed), (cross-eye), (glitch), (oversaturated), (overexposed), (underexposed), (bad proportions), (bad hands), (bad feet), (cloned face), (long neck), (missing arms), (missing legs), (extra fingers), (fused fingers), (poorly drawn hands), (poorly drawn face), (mutation), (deformed eyes), watermark, text, logo, signature, grainy, tiling, censored, nsfw, ugly, blurry eyes, noisy image, bad lighting, unnatural skin, asymmetry, cartoon, anime, drawing, painting, illustration, rendered, 3d, cgi, plastic, doll, fake"