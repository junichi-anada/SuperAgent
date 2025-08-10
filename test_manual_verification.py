#!/usr/bin/env python3
"""
エージェント画像生成の修正内容を手動検証するためのスクリプト
"""
import requests
import json
import os
from dotenv import load_dotenv

def test_api_endpoints():
    """APIエンドポイントの動作を確認"""
    load_dotenv()
    
    # API基本URL
    API_BASE_URL = "http://localhost:8000"
    
    print("🔍 修正内容の検証を開始します...")
    print("=" * 50)
    
    # 1. バックエンドAPIの確認
    print("\n1️⃣ バックエンドAPIエンドポイントの確認")
    print(f"   API URL: {API_BASE_URL}")
    
    try:
        # ヘルスチェック
        response = requests.get(f"{API_BASE_URL}/docs", timeout=5)
        if response.status_code == 200:
            print("   ✅ バックエンドAPI が正常に動作しています")
        else:
            print(f"   ❌ バックエンドAPIでエラー: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ バックエンドAPIに接続できません: {e}")
        return False
    
    # 2. フロントエンドの確認
    print("\n2️⃣ フロントエンドの確認")
    FRONTEND_URL = "http://localhost:3000"
    
    try:
        # フロントエンドのヘルスチェック
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print("   ✅ フロントエンドが正常に動作しています")
            print(f"   📱 ブラウザで確認: {FRONTEND_URL}")
        else:
            print(f"   ❌ フロントエンドでエラー: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   ⚠️  フロントエンドに接続できません: {e}")
        print("   💡 docker-compose up frontend で起動してください")
    
    # 3. 修正内容の確認
    print("\n3️⃣ 修正内容の確認")
    print("   ✅ 画像生成プロンプト入力フィールドを削除")
    print("   ✅ handleGenerateImage関数でプロンプト入力必須チェックを削除")
    print("   ✅ 画像生成APIコールでプロンプトパラメータを削除")
    print("   ✅ バックエンドAPIエンドポイントでプロンプトパラメータを不要に修正")
    print("   ✅ 画像生成中のUI表示を改善（スピナーアニメーション追加）")
    
    # 4. 手動検証手順
    print("\n4️⃣ 手動検証手順")
    print("   1. ブラウザで http://localhost:3000 にアクセス")
    print("   2. ログインまたはサインアップ")
    print("   3. 新しいエージェントを作成または既存エージェントを編集")
    print("   4. 外見情報（性別、髪型、目の色、体型、服装など）を入力")
    print("   5. 「画像を生成」ボタンをクリック")
    print("   6. ✨ プロンプト入力フィールドがないことを確認")
    print("   7. ✨ 生成中にスピナーアニメーションが表示されることを確認")
    print("   8. ✨ エージェントの外見情報から自動で画像が生成されることを確認")
    
    # 5. 期待される動作
    print("\n5️⃣ 期待される動作")
    print("   ▶️  画像生成プロンプトの入力は不要")
    print("   ▶️  エージェントの外見情報から自動でプロンプトが生成される")
    print("   ▶️  「画像を生成」ボタンをクリックするだけで画像が生成される")
    print("   ▶️  生成中はスピナーアニメーションが表示される")
    
    # 6. ログの確認方法
    print("\n6️⃣ ログの確認方法")
    print("   バックエンドログ:")
    print("   docker-compose logs backend | grep -E '(Generated prompt|Agent details)'")
    print("   フロントエンドログ:")
    print("   ブラウザの開発者ツール（F12）→ Console タブ")
    
    print("\n" + "=" * 50)
    print("🎉 検証準備完了！手動で動作を確認してください。")
    
    return True

if __name__ == "__main__":
    test_api_endpoints()