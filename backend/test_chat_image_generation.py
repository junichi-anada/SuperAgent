#!/usr/bin/env python3
"""
チャット内の画像生成機能をテストするスクリプト

このスクリプトは以下をテストします:
1. 画像生成リクエストの検出
2. WebSocket経由での画像生成
3. 生成された画像のURLが正しく返されるか
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
import aiohttp
import websockets
from pathlib import Path

# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from services.image_request_detector import ImageRequestDetector
from services.image_prompt_analyzer import ImagePromptAnalyzer

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 環境変数から設定を読み込み
API_URL = os.getenv("API_URL", "http://localhost:8000")
WS_URL = os.getenv("WS_URL", "ws://localhost:8000")

# テスト用の認証情報
TEST_USER = {
    "username": "test_user",
    "password": "test_password"
}

# 画像生成をトリガーするテストメッセージ
IMAGE_REQUEST_MESSAGES = [
    "写真を見せてください",
    "あなたの画像が欲しいです",
    "写真を送って",
    "全身の写真が見たい",
    "別角度の写真はありますか？",
    "今日の写真を見せて",
    "公園での写真が見たいです"
]

class ChatImageGenerationTester:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.agent_id = None
        self.chat_id = None
        self.image_detector = ImageRequestDetector()
        
    async def setup(self):
        """テスト環境のセットアップ"""
        logger.info("テスト環境をセットアップ中...")
        
        # 1. ユーザー登録/ログイン
        await self.authenticate()
        
        # 2. エージェントの作成/取得
        await self.setup_agent()
        
        # 3. チャットの作成
        await self.create_chat()
        
        logger.info("セットアップ完了")
        
    async def authenticate(self):
        """ユーザー認証"""
        async with aiohttp.ClientSession() as session:
            # まずサインアップを試行
            try:
                async with session.post(
                    f"{API_URL}/signup",
                    json=TEST_USER
                ) as response:
                    if response.status == 200:
                        logger.info("新規ユーザーを作成しました")
            except:
                pass
            
            # ログイン
            async with session.post(
                f"{API_URL}/login",
                json=TEST_USER
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.token = data["access_token"]
                    self.user_id = data["user"]["id"]
                    logger.info(f"ログイン成功: user_id={self.user_id}")
                else:
                    raise Exception(f"ログイン失敗: {response.status}")
    
    async def setup_agent(self):
        """テスト用エージェントの作成/取得"""
        headers = {"Authorization": f"Bearer {self.token}"}
        
        async with aiohttp.ClientSession() as session:
            # 既存のエージェントを確認
            async with session.get(
                f"{API_URL}/agents/",
                headers=headers
            ) as response:
                if response.status == 200:
                    agents = await response.json()
                    if agents:
                        self.agent_id = agents[0]["id"]
                        logger.info(f"既存のエージェントを使用: agent_id={self.agent_id}")
                        return
            
            # 新規エージェントを作成
            agent_data = {
                "name": "画像生成テストエージェント",
                "personality": "親切で写真を撮るのが好きなキャラクター",
                "description": "画像生成機能のテスト用エージェント",
                "gender": "female",
                "age": 25,
                "ethnicity": "Japanese",
                "hair_style": "long straight hair",
                "hair_color": "black",
                "eye_color": "brown",
                "body_type": "slim",
                "clothing": "casual modern outfit",
                "background": "modern city"
            }
            
            async with session.post(
                f"{API_URL}/agents/",
                headers=headers,
                json=agent_data
            ) as response:
                if response.status == 200:
                    agent = await response.json()
                    self.agent_id = agent["id"]
                    logger.info(f"新規エージェントを作成: agent_id={self.agent_id}")
                else:
                    raise Exception(f"エージェント作成失敗: {response.status}")
    
    async def create_chat(self):
        """チャットセッションの作成"""
        headers = {"Authorization": f"Bearer {self.token}"}
        
        async with aiohttp.ClientSession() as session:
            chat_data = {"agent_id": self.agent_id}
            
            async with session.post(
                f"{API_URL}/chats/",
                headers=headers,
                json=chat_data
            ) as response:
                if response.status == 200:
                    chat = await response.json()
                    self.chat_id = chat["id"]
                    logger.info(f"チャットを作成: chat_id={self.chat_id}")
                else:
                    raise Exception(f"チャット作成失敗: {response.status}")
    
    async def test_image_detection(self):
        """画像リクエスト検出のテスト"""
        logger.info("\n=== 画像リクエスト検出テスト ===")
        
        for message in IMAGE_REQUEST_MESSAGES:
            detected = self.image_detector.detect_image_request(message)
            context = self.image_detector.extract_image_context(message)
            image_type = self.image_detector.get_image_type_hint(message)
            
            logger.info(f"メッセージ: {message}")
            logger.info(f"  検出: {detected}")
            logger.info(f"  コンテキスト: {context}")
            logger.info(f"  画像タイプ: {image_type}")
            logger.info("")
    
    async def test_websocket_image_generation(self):
        """WebSocket経由での画像生成テスト"""
        logger.info("\n=== WebSocket画像生成テスト ===")
        
        ws_url = f"{WS_URL}/ws/chat/{self.chat_id}?token={self.token}"
        
        try:
            async with websockets.connect(ws_url) as websocket:
                logger.info("WebSocketに接続しました")
                
                # 各テストメッセージを送信
                for message in IMAGE_REQUEST_MESSAGES[:3]:  # 最初の3つだけテスト
                    logger.info(f"\n送信メッセージ: {message}")
                    
                    await websocket.send(json.dumps({
                        "content": message,
                        "timestamp": datetime.now().isoformat()
                    }))
                    
                    # 応答を待つ（最大30秒）
                    responses = []
                    start_time = asyncio.get_event_loop().time()
                    
                    while asyncio.get_event_loop().time() - start_time < 30:
                        try:
                            response = await asyncio.wait_for(
                                websocket.recv(),
                                timeout=1.0
                            )
                            data = json.loads(response)
                            responses.append(data)
                            
                            logger.info(f"受信: タイプ={data.get('type')}, "
                                      f"ステータス={data.get('status')}")
                            
                            # エラーチェック
                            if data.get("type") == "error":
                                logger.error(f"エラー: {data.get('message')}")
                                break
                            
                            # 完了チェック
                            if data.get("type") == "message" and data.get("status") == "completed":
                                logger.info(f"応答完了: {data.get('content', '')[:100]}...")
                                
                                # 画像URLの確認
                                if "image_url" in data:
                                    logger.info(f"画像URL: {data['image_url']}")
                                    
                                    # 画像が実際にアクセス可能か確認
                                    await self.verify_image_url(data['image_url'])
                                break
                                
                        except asyncio.TimeoutError:
                            continue
                    
                    # 少し待機
                    await asyncio.sleep(2)
                    
        except Exception as e:
            logger.error(f"WebSocketエラー: {e}")
            import traceback
            traceback.print_exc()
    
    async def verify_image_url(self, image_url):
        """生成された画像URLの検証"""
        try:
            # 相対URLを絶対URLに変換
            if image_url.startswith("/"):
                full_url = f"{API_URL}{image_url}"
            else:
                full_url = image_url
                
            async with aiohttp.ClientSession() as session:
                async with session.head(full_url) as response:
                    if response.status == 200:
                        logger.info(f"✓ 画像URLは有効です: {full_url}")
                    else:
                        logger.error(f"✗ 画像URLが無効です: {full_url} (status={response.status})")
        except Exception as e:
            logger.error(f"画像URL検証エラー: {e}")
    
    async def test_chat_history_with_images(self):
        """画像を含むチャット履歴の取得テスト"""
        logger.info("\n=== チャット履歴テスト ===")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_URL}/chats/{self.chat_id}/messages",
                headers=headers
            ) as response:
                if response.status == 200:
                    messages = await response.json()
                    
                    logger.info(f"メッセージ数: {len(messages)}")
                    
                    for msg in messages[-5:]:  # 最新5件を表示
                        logger.info(f"\n[{msg['sender']}] {msg['created_at']}")
                        logger.info(f"内容: {msg['content'][:100]}...")
                        
                        if msg.get('image_url'):
                            logger.info(f"画像: {msg['image_url']}")
                else:
                    logger.error(f"チャット履歴取得失敗: {response.status}")
    
    async def run_all_tests(self):
        """すべてのテストを実行"""
        try:
            await self.setup()
            await self.test_image_detection()
            await self.test_websocket_image_generation()
            await self.test_chat_history_with_images()
            
            logger.info("\n=== テスト完了 ===")
            logger.info("すべてのテストが正常に実行されました")
            
        except Exception as e:
            logger.error(f"テスト実行エラー: {e}")
            import traceback
            traceback.print_exc()

async def main():
    """メイン関数"""
    logger.info("チャット画像生成機能テストを開始します...")
    logger.info(f"API URL: {API_URL}")
    logger.info(f"WebSocket URL: {WS_URL}")
    
    tester = ChatImageGenerationTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())