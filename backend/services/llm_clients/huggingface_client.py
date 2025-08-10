import requests
import os
from typing import Dict, Any

class HuggingFaceClient:
    """Hugging Face Inference APIと通信するためのクライアント"""

    def __init__(self, api_key: str, model: str = "stabilityai/stable-diffusion-xl-base-1.0"):
        self.api_key = api_key
        self.base_url = "https://api-inference.huggingface.co/models/"
        self.model = model
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def generate_image(self, prompt: str, negative_prompt: str = None) -> bytes:
        """
        指定されたプロンプトから画像を生成します。

        Args:
            prompt (str): 画像生成のためのプロンプト。
            negative_prompt (str, optional): 生成を避けるべき要素。 Defaults to None.

        Returns:
            bytes: 生成された画像のバイナリデータ。
        
        Raises:
            Exception: API呼び出しに失敗した場合。
        """
        payload = {
            "inputs": prompt,
            "parameters": {
                "negative_prompt": negative_prompt,
            }
        }
        
        response = requests.post(
            f"{self.base_url}{self.model}",
            headers=self.headers,
            json=payload
        )
        
        if response.status_code == 200:
            return response.content
        else:
            raise Exception(f"Hugging Face API Error: {response.status_code} {response.text}")

def get_huggingface_client() -> HuggingFaceClient:
    """HuggingFaceClientのインスタンスを生成して返します。"""
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    
    if not api_key:
        raise ValueError("HUGGINGFACE_API_KEY environment variable not set.")
    return HuggingFaceClient(api_key=api_key)