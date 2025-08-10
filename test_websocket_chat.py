#!/usr/bin/env python3
import asyncio
import websockets
import json
import sys

async def test_chat(agent_id=1, message="こんにちは、調子はどうですか？"):
    uri = f"ws://localhost:8000/ws/{agent_id}"
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Connected to WebSocket: {uri}")
            
            # メッセージを送信
            await websocket.send(message)
            print(f"Sent message: {message}")
            
            # 応答を受信
            response = await websocket.recv()
            print(f"Received response: {response}")
            
            # WebSocketを閉じる
            await websocket.close()
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    agent_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    message = sys.argv[2] if len(sys.argv) > 2 else "こんにちは、調子はどうですか？"
    
    asyncio.run(test_chat(agent_id, message))