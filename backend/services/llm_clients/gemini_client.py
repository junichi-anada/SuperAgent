import os
import asyncio
from typing import Dict, Any
import google.generativeai as genai
from .base import LLMClientInterface

class GeminiClient(LLMClientInterface):
    """Google Gemini API クライアント"""

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-1.5-flash",
        temperature: float = 0.7,
        timeout: int = 60
    ):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.timeout = timeout
        genai.configure(api_key=self.api_key)
        self.genai_model = genai.GenerativeModel(self.model)

    async def generate(
        self,
        prompt: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Gemini APIを使用して応答を生成"""
        try:
            response = await asyncio.wait_for(
                self._call_api(prompt, **kwargs),
                timeout=self.timeout
            )
            
            return {
                "content": response.text,
                "model": self.model,
                "usage": {
                    # NOTE: Gemini API does not return token usage directly in the response object.
                    # This would need to be estimated or handled differently if required.
                    "prompt_tokens": None,
                    "completion_tokens": None,
                    "total_tokens": None,
                },
                "finish_reason": "stop" # Placeholder, Gemini API has different finish reasons
            }
        except asyncio.TimeoutError:
            raise TimeoutError(f"Gemini API timeout after {self.timeout} seconds")
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")

    async def _call_api(self, prompt: str, **kwargs) -> Any:
        """実際のAPI呼び出し"""
        generation_config = genai.types.GenerationConfig(
            temperature=kwargs.get("temperature", self.temperature)
        )
        return await self.genai_model.generate_content_async(
            prompt,
            generation_config=generation_config
        )

    async def validate_response(self, response: Dict[str, Any]) -> bool:
        """応答の妥当性を検証"""
        if not response.get("content"):
            return False
        if len(response["content"]) < 1:
            return False
        return True