#!/usr/bin/env python3
"""
Stable Diffusion WebUI統合テストスクリプト

このスクリプトは以下のテストを実行します：
1. WebUI APIの接続確認
2. モデル一覧の取得
3. 画像生成のテスト
4. エラーハンドリングのテスト
"""

import asyncio
import os
import sys
import logging
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.append(str(Path(__file__).parent))

from services.llm_clients.stable_diffusion_webui_client import StableDiffusionWebUIClient

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_webui_connection():
    """WebUI APIの接続確認"""
    print("🔗 WebUI API接続テスト開始...")
    
    client = StableDiffusionWebUIClient()
    
    try:
        # ヘルスチェック
        is_healthy = await client._check_api_health()
        if is_healthy:
            print("✅ WebUI APIに正常に接続できました")
            return True
        else:
            print("❌ WebUI APIに接続できません")
            return False
    except Exception as e:
        print(f"❌ 接続エラー: {e}")
        return False

async def test_get_models():
    """利用可能なモデル一覧の取得テスト"""
    print("\n📝 モデル一覧取得テスト開始...")
    
    client = StableDiffusionWebUIClient()
    
    try:
        models = await client._get_models()
        if models:
            print(f"✅ {len(models)}個のモデルが見つかりました:")
            for i, model in enumerate(models[:5]):  # 最初の5個のみ表示
                print(f"   {i+1}. {model.get('model_name', 'Unknown')}")
            if len(models) > 5:
                print(f"   ... 他 {len(models) - 5}個")
        else:
            print("⚠️  利用可能なモデルが見つかりません")
        return models
    except Exception as e:
        print(f"❌ モデル取得エラー: {e}")
        return []

async def test_select_model():
    """最適なモデル選択のテスト"""
    print("\n🎯 モデル選択テスト開始...")
    
    client = StableDiffusionWebUIClient()
    
    try:
        models = await client._get_models()
        if models:
            selected_model = await client._select_best_model(models)
            if selected_model:
                print(f"✅ 選択されたモデル: {selected_model}")
                return selected_model
            else:
                print("⚠️  適切なモデルが選択されませんでした")
        else:
            print("⚠️  テスト用モデルがありません")
        return None
    except Exception as e:
        print(f"❌ モデル選択エラー: {e}")
        return None

async def test_image_generation():
    """画像生成のテスト（軽量設定）"""
    print("\n🎨 画像生成テスト開始...")
    
    client = StableDiffusionWebUIClient()
    
    # テスト用プロンプト
    test_prompt = "a portrait of a beautiful woman, photorealistic, high quality"
    test_negative_prompt = "blurry, low quality, bad anatomy"
    
    try:
        print(f"プロンプト: {test_prompt}")
        
        # 軽量設定で画像生成
        image_data = await client.generate_image_async(
            prompt=test_prompt,
            negative_prompt=test_negative_prompt,
            width=512,  # 小さいサイズでテスト
            height=512,
            steps=10,   # 少ないステップでテスト
            cfg_scale=7.0
        )
        
        if image_data:
            # テスト画像を保存
            test_image_path = Path("test_webui_output.png")
            with open(test_image_path, "wb") as f:
                f.write(image_data)
            
            print(f"✅ 画像生成成功！サイズ: {len(image_data)} bytes")
            print(f"   保存先: {test_image_path}")
            return True
        else:
            print("❌ 画像データが空です")
            return False
            
    except Exception as e:
        print(f"❌ 画像生成エラー: {e}")
        return False

async def test_error_handling():
    """エラーハンドリングのテスト"""
    print("\n🛡️  エラーハンドリングテスト開始...")
    
    client = StableDiffusionWebUIClient()
    
    # 無効なプロンプトでテスト
    try:
        await client.generate_image_async(
            prompt="",  # 空のプロンプト
            width=64,   # 非常に小さいサイズ
            height=64,
            steps=1
        )
        print("⚠️  エラーが期待されましたが、処理が成功しました")
        return False
    except Exception as e:
        print(f"✅ 期待通りエラーが発生: {type(e).__name__}")
        return True

def test_sync_interface():
    """同期インターフェースのテスト"""
    print("\n🔄 同期インターフェーステスト開始...")
    
    client = StableDiffusionWebUIClient()
    
    try:
        # 同期メソッドをテスト（軽量設定）
        image_data = client.generate_image(
            prompt="simple test image",
            negative_prompt="blurry"
        )
        
        if image_data:
            print("✅ 同期インターフェース正常動作")
            return True
        else:
            print("❌ 同期インターフェースで画像データが空")
            return False
    except Exception as e:
        print(f"❌ 同期インターフェースエラー: {e}")
        return False

async def main():
    """メインテスト関数"""
    print("🚀 Stable Diffusion WebUI統合テスト開始\n")
    
    # 環境確認
    webui_url = os.getenv("WEBUI_API_URL", "http://stable-diffusion-webui:7860")
    print(f"WebUI URL: {webui_url}")
    
    test_results = []
    
    # 1. 接続テスト
    connection_ok = await test_webui_connection()
    test_results.append(("接続テスト", connection_ok))
    
    if not connection_ok:
        print("\n❌ WebUI APIに接続できないため、他のテストをスキップします")
        print("📝 Dockerコンテナが起動していることを確認してください:")
        print("   docker-compose up --profile gpu stable-diffusion-webui")
        return
    
    # 2. モデルテスト
    models = await test_get_models()
    test_results.append(("モデル取得", len(models) > 0))
    
    # 3. モデル選択テスト
    selected_model = await test_select_model()
    test_results.append(("モデル選択", selected_model is not None))
    
    # 4. 画像生成テスト（非同期）
    generation_ok = await test_image_generation()
    test_results.append(("画像生成（非同期）", generation_ok))
    
    # 5. エラーハンドリングテスト
    error_handling_ok = await test_error_handling()
    test_results.append(("エラーハンドリング", error_handling_ok))
    
    # 6. 同期インターフェーステスト
    sync_ok = test_sync_interface()
    test_results.append(("同期インターフェース", sync_ok))
    
    # 結果まとめ
    print("\n" + "="*50)
    print("📊 テスト結果サマリー")
    print("="*50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} : {status}")
        if result:
            passed += 1
    
    print("-"*50)
    print(f"合計: {passed}/{total} テスト通過")
    
    if passed == total:
        print("🎉 すべてのテストが成功しました！")
        print("Stable Diffusion WebUIが正常に統合されています。")
    else:
        print("⚠️  一部のテストが失敗しました。")
        print("設定やDockerコンテナの状態を確認してください。")

if __name__ == "__main__":
    asyncio.run(main())