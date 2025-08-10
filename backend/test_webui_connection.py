#!/usr/bin/env python3
import httpx
import asyncio
import os

async def test_connection():
    url = os.getenv("WEBUI_API_URL", "http://stable-diffusion-webui-cpu:8080")
    print(f"Testing connection to: {url}")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test health endpoint
            response = await client.get(f"{url}/sdapi/v1/progress")
            print(f"Progress endpoint status: {response.status_code}")
            if response.status_code == 200:
                print("Progress data:", response.json())
            
            # Test models endpoint
            response = await client.get(f"{url}/sdapi/v1/sd-models")
            print(f"\nModels endpoint status: {response.status_code}")
            if response.status_code == 200:
                models = response.json()
                print(f"Available models: {len(models)}")
                for model in models:
                    print(f"  - {model.get('model_name', 'Unknown')}")
            
            print("\nConnection test successful!")
            
    except Exception as e:
        print(f"Connection failed: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())