import os
import json
import base64
import logging
import asyncio
from typing import Optional, Dict, Any, Callable, Awaitable, Tuple
from io import BytesIO
import httpx
from PIL import Image


logger = logging.getLogger(__name__)

class StableDiffusionWebUIClient:
    """Stable Diffusion WebUI API クライアント"""
    
    def __init__(self):
        self.base_url = os.getenv("WEBUI_API_URL", "http://stable-diffusion-webui:7860")
        self.timeout = int(os.getenv("WEBUI_TIMEOUT", "600"))  # タイムアウトを環境変数から取得（デフォルト10分）
        logger.info(f"Initialized Stable Diffusion WebUI client with base URL: {self.base_url} and timeout: {self.timeout}s")
    
    async def _check_api_health(self) -> bool:
        """WebUI APIの状態をチェック"""
        try:
            logger.info(f"Checking WebUI API health at: {self.base_url}/sdapi/v1/progress")
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/sdapi/v1/progress")
                logger.info(f"Health check response: {response.status_code}")
                return response.status_code == 200
        except httpx.ConnectError as e:
            logger.error(f"WebUI API connection error: {e}")
            return False
        except Exception as e:
            logger.error(f"WebUI API health check failed: {type(e).__name__}: {e}")
            return False
    
    async def get_progress_async(self) -> Dict[str, Any]:
        """WebUI APIから現在の進捗状況を取得"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # skip_current_image=false をつけて、プレビュー画像を含めないようにする
                response = await client.get(f"{self.base_url}/sdapi/v1/progress?skip_current_image=false")
                if response.status_code == 200:
                    return response.json()
                return {}
        except Exception as e:
            logger.warning(f"Failed to get progress: {e}")
            return {}

    async def _get_models(self) -> list:
        """利用可能なモデル一覧を取得"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.base_url}/sdapi/v1/sd-models")
                if response.status_code == 200:
                    models = response.json()
                    logger.info(f"Found {len(models)} available models")
                    return models
                else:
                    logger.warning(f"Failed to get models: {response.status_code}")
                    return []
        except Exception as e:
            logger.error(f"Error getting models: {e}")
            return []
    
    async def _select_best_model(self, models: list) -> Optional[str]:
        """最適なモデルを選択（アダルトコンテンツ対応重視）"""
        if not models:
            return None
        
        # アダルトコンテンツに適したモデルの優先順位
        preferred_models = [
            "yayoi_mix_v28beta",
            "yayoi_mix",
            "yayoi",
            "chilloutmix",
            "realisticvision",
            "anything",
            "nai",
            "waifu",
            "counterfeit"
        ]
        
        # 利用可能なモデル名を小文字で取得
        available_models = [model.get("model_name", "").lower() for model in models]
        
        # 優先順位に従って選択
        for preferred in preferred_models:
            for available in available_models:
                if preferred in available:
                    original_name = next(
                        model["model_name"] for model in models 
                        if model["model_name"].lower() == available
                    )
                    logger.info(f"Selected model: {original_name}")
                    return original_name
        
        # 優先モデルが見つからない場合は最初のモデルを使用
        default_model = models["model_name"]
        logger.info(f"Using default model: {default_model}")
        return default_model
    
    def generate_image(self, prompt: str, negative_prompt: str = "", **kwargs) -> bytes:
        """同期的な画像生成（既存インターフェース互換）"""
        image_data, _ = asyncio.run(self.generate_image_async(prompt, negative_prompt, **kwargs))
        return image_data
    
    async def generate_image_async(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 512,
        height: int = 512,
        steps: int = 25,
        cfg_scale: float = 7.0,
        sampler_name: str = "DPM++ 2M Karras",
        progress_callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None,
        seed: Optional[int] = None,
        ip_adapter_image_url: Optional[str] = None,
        **kwargs
    ) -> Tuple[bytes, int]:
        """非同期画像生成（進捗コールバック、IP-Adapter対応）"""

        # APIの状態チェック
        if not await self._check_api_health():
            raise Exception("Stable Diffusion WebUI API is not available")

        # 利用可能なモデルを取得して最適なものを選択
        models = await self._get_models()
        selected_model = await self._select_best_model(models)

        # リクエストペイロード
        payload = {
            "prompt": prompt.replace("(selfie:1.3)", "(selfie:1.3), (upper body:1.3)"),
            "negative_prompt": negative_prompt,
            "width": 480,
            "height": 640,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "sampler_name": sampler_name,
            "restore_faces": True,
            "tiling": False,
            "do_not_save_samples": True,
            "do_not_save_grid": True,
            "enable_hr": False,  # Hi-res fix
            "seed": seed if seed is not None and seed > 0 else -1,
            "batch_size": 1,
            "n_iter": 1,
        }

        # IP-Adapterが指定されている場合
        if ip_adapter_image_url:
            logger.info(f"Using IP-Adapter with image: {ip_adapter_image_url}")
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(ip_adapter_image_url)
                    response.raise_for_status()
                    image_data = response.content
                    encoded_image = base64.b64encode(image_data).decode('utf-8')

                payload["alwayson_scripts"] = {
                    "controlnet": {
                        "args": [
                            {
                                "input_image": encoded_image,
                                "module": "ip-adapter_clip_sd15",
                                "model": "ip-adapter-plus-face_sd15 [7516cac4]",
                                "weight": 1.0,
                                "resize_mode": "Crop and Resize",
                            }
                        ]
                    }
                }
                logger.info("Successfully added IP-Adapter payload")
            except Exception as e:
                logger.error(f"Failed to process IP-Adapter image: {e}")
                # IP-Adapterに失敗しても、通常の画像生成は続行する
                pass

        # モデルが指定されている場合は切り替え
        if selected_model:
            await self._switch_model(selected_model)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"Generating image with prompt: {prompt[:100]}...")

                # txt2imgリクエストをタスクとして開始
                generation_task = asyncio.create_task(client.post(
                    f"{self.base_url}/sdapi/v1/txt2img",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ))

                # 生成タスクが完了するまで進捗をポーリング
                while not generation_task.done():
                    if progress_callback:
                        progress_data = await self.get_progress_async()
                        if progress_data and progress_data.get("progress", 0) > 0:
                            await progress_callback(progress_data)
                    await asyncio.sleep(1)

                response = await generation_task

                if response.status_code != 200:
                    error_msg = f"WebUI API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    raise Exception(error_msg)

                result = response.json()

                # 生成された画像を取得
                if "images" not in result or not result["images"][0]:
                    raise Exception("No images generated")

                # レスポンスからシード値を取得
                try:
                    # infoフィールドはJSON文字列または辞書オブジェクト
                    info_data = result.get("info")
                    info = {}
                    if isinstance(info_data, str) and info_data:
                        try:
                            info = json.loads(info_data)
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to decode info JSON: {info_data}")
                    elif isinstance(info_data, dict):
                        info = info_data
                    
                    response_seed = info.get("seed", -1)
                    logger.info(f"Generated image with seed: {response_seed}")
                except Exception as e:
                    logger.warning(f"Could not extract seed from response: {e}. Info field: {result.get('info')}")
                    response_seed = -1

                # Base64デコード
                image_b64 = result["images"][0]
                image_data = base64.b64decode(image_b64)

                # 画像の検証
                try:
                    image = Image.open(BytesIO(image_data))
                    image.verify()
                    logger.info(f"Successfully generated image: {image.size}")
                except Exception as e:
                    raise Exception(f"Generated image is invalid: {e}")

                return image_data, response_seed

        except httpx.TimeoutException:
            raise Exception("Image generation timed out")
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            raise Exception(f"Failed to generate image: {str(e)}")
    
    async def _switch_model(self, model_name: str) -> bool:
        """モデルを切り替え"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                payload = {
                    "sd_model_name": model_name
                }
                
                response = await client.post(
                    f"{self.base_url}/sdapi/v1/options",
                    json=payload
                )
                
                if response.status_code == 200:
                    logger.info(f"Successfully switched to model: {model_name}")
                    # モデル切り替え後の待機時間
                    await asyncio.sleep(2)
                    return True
                else:
                    logger.warning(f"Failed to switch model: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error switching model: {e}")
            return False
    
    async def get_available_samplers(self) -> list:
        """利用可能なサンプラー一覧を取得"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.base_url}/sdapi/v1/samplers")
                if response.status_code == 200:
                    return response.json()
                return []
        except Exception as e:
            logger.error(f"Error getting samplers: {e}")
            return []


def get_stable_diffusion_webui_client() -> StableDiffusionWebUIClient:
    """Stable Diffusion WebUI クライアントのファクトリ関数"""
    return StableDiffusionWebUIClient()