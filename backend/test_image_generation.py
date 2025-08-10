import os
from dotenv import load_dotenv
from services.llm_clients.modelslab_client import ModelsLabClient

def test_modelslab_client():
    """
    ModelsLabクライアントの画像生成をテストします。
    """
    # .envファイルをロードして環境変数を設定
    print("Loading .env file...")
    load_dotenv()

    try:
        # ModelsLabClientをインスタンス化
        print("Initializing ModelsLabClient...")
        client = ModelsLabClient()
        
        print(f"API Key: {client.api_key[:10]}...")
        print(f"Model ID: {client.model_id}")
        print(f"API URL: {client.api_url}")

        # 画像生成のプロンプト
        prompt = "A portrait of a friendly young woman, 25 years old, brown hair, blue eyes, smiling, digital art, high quality"
        negative_prompt = "low quality, blurry, distorted, ugly, bad anatomy"
        
        print(f"Generating image with prompt: '{prompt[:50]}...' using ModelsLab provider...")
        
        # 画像を生成
        image_data = client.generate_image(prompt, negative_prompt)

        # 結果を検証
        print("Asserting generated image data...")
        assert isinstance(image_data, bytes), f"Expected image data to be bytes, but got {type(image_data)}."
        assert image_data, "Generated image data is empty."
        assert len(image_data) > 1000, f"Image data seems too small: {len(image_data)} bytes"

        print(f"\n✅ Test successful: Image generated successfully using ModelsLab provider.")
        print(f"   Image size: {len(image_data)} bytes")

    except Exception as e:
        print(f"\n❌ Test failed: An error occurred during image generation.")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_modelslab_client()