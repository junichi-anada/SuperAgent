#!/usr/bin/env python3
import httpx
import asyncio
import os
import json

async def disable_xformers():
    url = os.getenv("WEBUI_API_URL", "http://stable-diffusion-webui-cpu:8080")
    print(f"Disabling xformers at: {url}")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # WebUIのオプションを確認
            response = await client.get(f"{url}/sdapi/v1/options")
            if response.status_code == 200:
                options = response.json()
                print("Current options:", json.dumps(options, indent=2)[:500])
                
                # xformersを無効化するオプションを設定
                new_options = {
                    "sd_model_checkpoint": options.get("sd_model_checkpoint", "v1-5-pruned-emaonly"),
                    "CLIP_stop_at_last_layers": 1,
                    "enable_hr": False,
                    "sdxl_crop_top": 0,
                    "sdxl_crop_left": 0,
                    "sdxl_refiner_low_aesthetic_score": 2.5,
                    "sdxl_refiner_high_aesthetic_score": 6.0,
                }
                
                # オプションを更新
                response = await client.post(f"{url}/sdapi/v1/options", json=new_options)
                print(f"Options update status: {response.status_code}")
                if response.status_code != 200:
                    print(f"Response: {response.text}")
                
                print("Successfully updated options")
            else:
                print(f"Failed to get options: {response.status_code}")
                
    except Exception as e:
        print(f"Failed to disable xformers: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(disable_xformers())