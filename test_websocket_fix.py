#!/usr/bin/env python3
"""
WebSocket接続修正のテストスクリプト
"""
import asyncio
import websockets
import json
import sys

async def test_websocket_connection():
    # テスト用のチャットID（実際のIDに置き換えてください）
    chat_id = 1
    
    # WebSocket URL
    ws_url = f"ws://localhost:8000/api/v1/chats/ws/{chat_id}"
    
    print(f"WebSocket接続テスト開始: {ws_url}")
    
    try:
        async with websockets.connect(ws_url) as websocket:
            print("✅ WebSocket接続成功!")
            
            # テストメッセージを送信
            test_message = {
                "content": "これはWebSocket接続テストです"
            }
            
            await websocket.send(json.dumps(test_message))
            print(f"📤 メッセージ送信: {test_message['content']}")
            
            # レスポンスを待つ
            response_count = 0
            while response_count < 3:  # 最大3つのレスポンスを待つ
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    data = json.loads(response)
                    print(f"📥 レスポンス受信: {json.dumps(data, ensure_ascii=False, indent=2)}")
                    response_count += 1
                    
                    # AIの応答が含まれていれば成功
                    if data.get("sender") == "ai" and not data.get("type"):
                        print("\n✅ WebSocket通信テスト成功！")
                        return True
                        
                except asyncio.TimeoutError:
                    print("⏱️ タイムアウト: 10秒以内にレスポンスがありませんでした")
                    break
                    
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        return False
    
    return False

async def main():
    print("WebSocket接続修正のテスト")
    print("=" * 50)
    print("注意: このテストを実行する前に以下を確認してください:")
    print("1. Dockerコンテナが起動している")
    print("2. データベースにテスト用のチャットが存在する")
    print("3. バックエンドサーバーが正常に動作している")
    print("=" * 50)
    
    success = await test_websocket_connection()
    
    if success:
        print("\n🎉 修正が正常に動作しています！")
        sys.exit(0)
    else:
        print("\n⚠️ WebSocket接続に問題があります。ログを確認してください。")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())