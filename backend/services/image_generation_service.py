import os
import uuid
import logging
import traceback
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
from io import BytesIO
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session

import crud
from models import Agent
from database import SessionLocal
from services.llm_clients.huggingface_client import get_huggingface_client
from services.llm_clients.modelslab_client import ModelsLabClient
from services.llm_clients.stable_diffusion_webui_client import get_stable_diffusion_webui_client

logger = logging.getLogger(__name__)

class ImageGenerationService:
    """画像生成と保存を管理するサービス"""

    def __init__(self):
        self.backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        self.storage_path = Path("backend/static/agent_images")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.fallback_image_url = "/static/fallback_agent.png"
        self.generation_logs = {}  # 生成ログを一時的に保存
        
        # プロバイダーの決定：環境変数 > デフォルト
        provider = os.getenv("IMAGE_GENERATION_PROVIDER", "huggingface")

        try:
            if provider == "modelslab":
                self.client = ModelsLabClient()
                logger.info("ModelsLab client initialized successfully.")
            elif provider == "webui":
                self.client = get_stable_diffusion_webui_client()
                logger.info("Stable Diffusion WebUI client initialized successfully.")
            else:
                self.client = get_huggingface_client()
                logger.info("Hugging Face client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize image generation client for provider {provider}: {e}")
            self.client = None

    def _generate_prompt(self, agent: Agent) -> str:
        """エージェントの属性から画像生成用のプロンプトを作成します。"""
        details = [
            agent.gender,
            agent.ethnicity,
            f"{agent.age} years old",
            agent.hair_style,
            f"{agent.eye_color} eyes",
            agent.body_type,
            f"wearing {agent.clothing}",
        ]
        
        # リアルな写真風のプロンプトを構築
        prompt = "R3alisticF, "
        prompt += f"a portrait of a {', '.join(filter(None, details))}, "
        prompt += f"background: {agent.background}, "
        prompt += "High Detail, Perfect Composition, high contrast, photorealistic, "
        prompt += "professional photography, studio lighting, sharp focus, detailed skin texture, "
        prompt += "realistic lighting, natural pose, high resolution, masterpiece"
        
        logger.info(f"Generated prompt from agent attributes: {prompt}")
        logger.info(f"Agent details - Gender: {agent.gender}, Ethnicity: {agent.ethnicity}, Age: {agent.age}, Hair: {agent.hair_style}, Eyes: {agent.eye_color}, Body: {agent.body_type}, Clothing: {agent.clothing}")
        
        return prompt

    def _generate_negative_prompt(self) -> str:
        """ネガティブプロンプトを返します。"""
        return "(worst quality:2), (low quality:2), (normal quality:2), (jpeg artifacts), (blurry), (duplicate), (morbid), (mutilated), (out of frame), (extra limbs), (bad anatomy), (disfigured), (deformed), (cross-eye), (glitch), (oversaturated), (overexposed), (underexposed), (bad proportions), (bad hands), (bad feet), (cloned face), (long neck), (missing arms), (missing legs), (extra fingers), (fused fingers), (poorly drawn hands), (poorly drawn face), (mutation), (deformed eyes), watermark, text, logo, signature, grainy, tiling, censored, nsfw, ugly, blurry eyes, noisy image, bad lighting, unnatural skin, asymmetry, cartoon, anime, drawing, painting, illustration, rendered, 3d, cgi, plastic, doll, fake"

    def _remove_old_image(self, image_url: Optional[str]) -> None:
        """古い画像ファイルを削除します。"""
        if not image_url or image_url == self.fallback_image_url:
            return
        
        try:
            # URLからファイルパスを抽出
            if image_url.startswith("/static/agent_images/"):
                filename = image_url.split("/")[-1]
                file_path = self.storage_path / filename
                if file_path.exists():
                    file_path.unlink()
                    logger.info(f"Removed old image: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to remove old image: {e}")

    def get_generation_log(self, agent_id: int) -> Optional[Dict[str, Any]]:
        """エージェントの画像生成ログを取得"""
        return self.generation_logs.get(agent_id)

    async def _generate_and_save_image_internal(
        self,
        db: Session,
        agent: Agent,
        prompt: str,
        force_regenerate: bool = False,
        user_message: Optional[str] = None,
        keywords: Optional[str] = None,
        message_id: Optional[int] = None
    ):
        """画像生成のコアロジック"""
        agent_id = agent.id
        # 生成ログを初期化
        self.generation_logs[agent_id] = {
            "status": "started",
            "started_at": datetime.now().isoformat(),
            "provider": self.client.__class__.__name__ if self.client else "Unknown",
            "steps": [],
            "progress": 0.0,
        }

        if agent.image_url and not force_regenerate:
            logger.info(f"Using cached image for agent {agent_id}: {agent.image_url}")
            self.generation_logs[agent_id].update({
                "status": "cached",
                "steps": [{"step": "cache_check", "status": "cached", "message": "Using existing image", "timestamp": datetime.now().isoformat()}]
            })
            return agent.image_url, agent.image_seed

        # プロンプト生成
        self.generation_logs[agent_id]["steps"].append({"step": "prompt_generation", "status": "started", "timestamp": datetime.now().isoformat()})
        negative_prompt = self._generate_negative_prompt()
        self.generation_logs[agent_id].update({"prompt": prompt, "negative_prompt": negative_prompt})
        self.generation_logs[agent_id]["steps"][-1].update({"status": "completed", "message": "Prompt generated successfully"})

        if not self.client:
            logger.error("Image generation client is not available.")
            self.generation_logs[agent_id].update({"status": "failed", "error": "Image generation service is not available."})
            raise HTTPException(status_code=503, detail="Image generation service is not available.")

        # 進捗更新用のコールバック
        async def progress_callback(progress_data: Dict[str, Any]):
            progress = progress_data.get("progress", 0) * 100
            self.generation_logs[agent_id]["progress"] = round(progress, 1)
            logger.debug(f"Agent {agent_id} progress: {progress:.1f}%")

        try:
            self.generation_logs[agent_id]["steps"].append({"step": "image_generation", "status": "started", "timestamp": datetime.now().isoformat(), "provider": self.client.__class__.__name__})
            logger.info(f"Generating image for agent {agent_id} with prompt: {prompt}")
            
            generation_start = datetime.now()
            
            # IP-Adapter用の引数を準備
            ip_adapter_kwargs = {}
            ip_adapter_model = None
            if isinstance(self.client, get_stable_diffusion_webui_client().__class__) and agent.image_url:
                ip_adapter_kwargs['ip_adapter_image_url'] = agent.image_url
                # This is a simplification. You might want to get the actual model name from the client
                ip_adapter_model = "default_ip_adapter"

            image_data, generated_seed = await self.client.generate_image_async(
                prompt=prompt,
                negative_prompt=negative_prompt,
                progress_callback=progress_callback,
                seed=agent.image_seed if not force_regenerate else None,
                **ip_adapter_kwargs
            )
            
            generation_time = (datetime.now() - generation_start).total_seconds()

            logger.info(f"Successfully generated image for agent {agent_id}")
            self.generation_logs[agent_id]["steps"][-1].update({"status": "completed", "message": "Image generated successfully", "generation_time": f"{generation_time:.2f}s"})

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to generate image for agent {agent_id}: {e}\n{traceback.format_exc()}")
            self.generation_logs[agent_id].update({"status": "failed", "error": error_msg})
            self.generation_logs[agent_id]["steps"][-1].update({"status": "failed", "error": error_msg})
            raise HTTPException(status_code=500, detail=f"Failed to generate image: {error_msg}")

        if force_regenerate and agent.image_url:
            self._remove_old_image(agent.image_url)

        filename = f"{uuid.uuid4()}.png"
        file_path = self.storage_path / filename
        
        self.generation_logs[agent_id]["steps"].append({"step": "save_image", "status": "started", "timestamp": datetime.now().isoformat()})
        try:
            with open(file_path, "wb") as f:
                f.write(image_data)
            logger.info(f"Saved image for agent {agent_id}: {file_path}")
            self.generation_logs[agent_id]["steps"][-1].update({"status": "completed", "message": f"Image saved as {filename}"})
        except Exception as e:
            logger.error(f"Failed to save image file: {e}")
            self.generation_logs[agent_id].update({"status": "failed", "error": str(e)})
            self.generation_logs[agent_id]["steps"][-1].update({"status": "failed", "error": str(e)})
            raise HTTPException(status_code=500, detail=f"Failed to save image: {e}")
        
        # 完全なURLを生成
        relative_path = file_path.relative_to(Path("backend/static"))
        image_url = f"{self.backend_url}/static/{relative_path}"
        
        # データベースにログを保存
        if user_message and prompt:
            log_entry = schemas.ImageGenerationLogCreate(
                agent_id=agent_id,
                message_id=message_id,
                user_message=user_message,
                keywords=keywords,
                model=self.client.__class__.__name__,
                prompt=prompt,
                ip_adapter_model=ip_adapter_model,
                image_url=image_url
            )
            crud.create_image_generation_log(db, log=log_entry)

        self.generation_logs[agent_id].update({
            "status": "completed",
            "completed_at": datetime.now().isoformat(),
            "image_url": image_url,
            "image_seed": generated_seed,
            "progress": 100.0
        })
        total_time = (datetime.fromisoformat(self.generation_logs[agent_id]["completed_at"]) -
                     datetime.fromisoformat(self.generation_logs[agent_id]["started_at"])).total_seconds()
        self.generation_logs[agent_id]["total_time"] = f"{total_time:.2f}s"
        
        return image_url, generated_seed

    async def generate_and_save_image(self, agent_id: int, user_id: int, force_regenerate: bool = False):
        """エージェントのプロフィール画像などを生成します。"""
        db: Session = SessionLocal()
        try:
            agent = crud.get_agent(db, agent_id=agent_id, user_id=user_id)
            if not agent:
                logger.error(f"Agent not found for id: {agent_id} and user: {user_id}")
                raise HTTPException(status_code=404, detail="Agent not found")

            prompt = self._generate_prompt(agent)
            
            image_url, generated_seed = await self._generate_and_save_image_internal(
                db=db,
                agent=agent,
                prompt=prompt,
                force_regenerate=force_regenerate
            )
            
            # Update agent's primary image
            crud.create_agent_image(db, agent_id=agent_id, image_url=image_url, is_primary=True, image_seed=generated_seed)
            
        finally:
            db.close()

    async def generate_image_in_chat(
        self,
        db: Session,
        agent: Agent,
        prompt: str,
        user_message: str,
        keywords: str,
        chat_id: int,
        message_id: int,
        force_regenerate: bool = False
    ):
        """チャットの文脈で画像を生成し、メッセージとして保存します。"""
        image_url, generated_seed = await self._generate_and_save_image_internal(
            db=db,
            agent=agent,
            prompt=prompt,
            force_regenerate=force_regenerate,
            user_message=user_message,
            keywords=keywords,
            message_id=message_id
        )

        # Update message with image url
        message = crud.get_message(db, message_id) # crudにget_messageがないので追加する必要がある
        if message:
            message.image_url = image_url
            db.commit()
            db.refresh(message)
        
        return image_url, generated_seed
