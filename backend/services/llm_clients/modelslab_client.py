import os
import requests
import json
import logging
import time

logger = logging.getLogger(__name__)

class ModelsLabClient:
    """A client for interacting with the ModelsLab API."""

    def __init__(self):
        """
        Initializes the ModelsLabClient, loading the API key and model ID
        from environment variables.
        """
        self.api_key = os.getenv("MODELSLAB_API_KEY")
        self.model_id = os.getenv("MODELSLAB_MODEL_ID")

        if not self.api_key:
            raise ValueError("The MODELSLAB_API_KEY environment variable is not set.")
        if not self.model_id:
            raise ValueError("The MODELSLAB_MODEL_ID environment variable is not set.")

        self.api_url = "https://modelslab.com/api/v6/images/text2img"
        self.headers = {
            "key": self.api_key,
            "Content-Type": "application/json"
        }

    def generate_image(self, prompt: str, negative_prompt: str = None) -> bytes:
        """
        Generates an image based on the provided prompt.

        Args:
            prompt: The text prompt to generate the image from.
            negative_prompt: The negative prompt to avoid certain elements.

        Returns:
            The generated image data as bytes.

        Raises:
            Exception: If the API call fails.
        """
        # デフォルトのネガティブプロンプト
        if negative_prompt is None:
            negative_prompt = "(worst quality:2), (low quality:2), (normal quality:2), (jpeg artifacts), (blurry), (duplicate), (morbid), (mutilated), (out of frame), (extra limbs), (bad anatomy), (disfigured), (deformed), (cross-eye), (glitch), (oversaturated), (overexposed), (underexposed), (bad proportions), (bad hands), (bad feet), (cloned face), (long neck), (missing arms), (missing legs), (extra fingers), (fused fingers), (poorly drawn hands), (poorly drawn face), (mutation), (deformed eyes), watermark, text, logo, signature, grainy, tiling, censored, nsfw, ugly, blurry eyes, noisy image, bad lighting, unnatural skin, asymmetry"

        payload = {
            "key": self.api_key,
            "prompt": prompt,
            "model_id": self.model_id,
            "lora_model": None,
            "width": "1024",
            "height": "1024",
            "negative_prompt": negative_prompt,
            "num_inference_steps": "31",
            "scheduler": "DPMSolverMultistepScheduler",
            "guidance_scale": "7.5",
            "enhance_prompt": None
        }

        print(f"Sending request to ModelsLab API...")
        print(f"API URL: {self.api_url}")
        print(f"Headers: {self.headers}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            print(f"Response status code: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            print(f"Raw response text: {response.text}")
            
            response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
            
            result = response.json()
            print(f"Parsed JSON response: {json.dumps(result, indent=2)}")
            
            # レスポンスの構造を確認
            if result.get("status") == "success":
                # 画像URLを取得
                if "output" in result and result["output"]:
                    image_url = result["output"][0] if isinstance(result["output"], list) else result["output"]
                    
                    # 画像データをダウンロード
                    print(f"Downloading image from URL: {image_url}")
                    image_response = requests.get(image_url)
                    image_response.raise_for_status()
                    
                    return image_response.content
                else:
                    raise Exception("No image output in API response")
            elif result.get("status") == "processing":
                # 非同期処理の場合、future_linksから画像URLを取得
                print(f"Image is processing. ETA: {result.get('eta', 'unknown')} seconds")
                
                # future_linksまたはmeta.outputから画像URLを取得
                image_url = None
                if result.get("future_links") and result["future_links"]:
                    image_url = result["future_links"][0]
                elif result.get("meta", {}).get("output") and result["meta"]["output"]:
                    image_url = result["meta"]["output"][0]
                
                if not image_url:
                    raise Exception("No image URL provided in processing response")
                
                print(f"Using future link URL: {image_url}")
                
                # 画像が準備されるまで少し待つ
                print("Waiting for image to be ready...")
                time.sleep(3)  # 3秒待機
                
                # 画像データをダウンロード
                print(f"Downloading image from URL: {image_url}")
                image_response = requests.get(image_url)
                
                # 画像がまだ準備できていない場合は、もう少し待つ
                if image_response.status_code == 404:
                    print("Image not ready yet, waiting 5 more seconds...")
                    time.sleep(5)
                    image_response = requests.get(image_url)
                
                image_response.raise_for_status()
                return image_response.content
            else:
                error_message = result.get("message", result.get("messege", "Unknown error"))
                raise Exception(f"ModelsLab API error: {error_message}")
                
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err} - {response.text}")
            raise Exception(f"Failed to generate image with ModelsLab API: HTTP {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as req_err:
            logger.error(f"Request error occurred: {req_err}")
            raise Exception(f"Failed to generate image with ModelsLab API: {req_err}")
        except Exception as err:
            logger.error(f"Other error occurred: {err}")
            raise Exception(f"Failed to generate image with ModelsLab API: {err}")