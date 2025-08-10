#!/usr/bin/env python3
import asyncio
import os
import sys
sys.path.append('/app')

from services.image_generation_service import ImageGenerationService
from services.llm_clients.stable_diffusion_webui_client import StableDiffusionWebUIClient

async def test_image_generation():
    print("Testing image generation...")
    
    # Initialize client
    client = StableDiffusionWebUIClient()
    
    # Test simple image generation
    prompt = "a beautiful landscape, mountains, sunset"
    negative_prompt = "low quality, blurry"
    
    try:
        print(f"Generating image with prompt: {prompt}")
        image_data = await client.generate_image_async(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=256,
            height=256,
            steps=10
        )
        print(f"Image generated successfully! Size: {len(image_data)} bytes")
        return True
    except Exception as e:
        print(f"Image generation failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_image_generation())
    sys.exit(0 if success else 1)