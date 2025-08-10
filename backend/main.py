from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import auth, agents, chat, tags
import os
from database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from services.llm_service import LLMService
from services.image_generation_service import ImageGenerationService
from dependencies import get_llm_service
import logging
import json

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    app.state.image_generation_service = ImageGenerationService()

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create static directory if it doesn't exist
if not os.path.exists("backend/static"):
    os.makedirs("backend/static/agent_images", exist_ok=True)

app.mount("/static", StaticFiles(directory="backend/static"), name="static_files")

app.include_router(auth.router, prefix="/api/v1")
app.include_router(agents.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(tags.router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"message": "Backend is running!"}

@app.get("/api/v1/poc/call-ollama")
async def call_ollama_poc():
    return {"service": "ollama", "status": "mock_ok"}


@app.get("/api/v1/poc/call-comfyui")
async def call_comfyui_poc():
    return {"service": "comfyui", "status": "mock_ok"}


@app.websocket("/ws/{agent_id}")
async def websocket_test_endpoint(
    websocket: WebSocket,
    agent_id: int,
    db: Session = Depends(get_db),
    llm_service: LLMService = Depends(get_llm_service)
):
    """テスト用のWebSocketエンドポイント（認証なし）"""
    await websocket.accept()
    try:
        while True:
            # メッセージを受信
            message = await websocket.receive_text()
            
            # 応答を生成
            try:
                response = await llm_service.generate_response(
                    db=db,
                    message=message,
                    agent_id=agent_id,
                    chat_id=None,  # テスト用なのでchat_idは使用しない
                )
                
                # エラーチェック
                if response.get("error"):
                    await websocket.send_text(json.dumps(response))
                else:
                    # 正常な応答を送信
                    await websocket.send_text(response["content"])
                    
            except Exception as e:
                # エラーレスポンスを送信
                error_response = {
                    "error": True,
                    "content": f"エラーが発生しました: {str(e)}"
                }
                await websocket.send_text(json.dumps(error_response))
                
    except WebSocketDisconnect:
        pass
