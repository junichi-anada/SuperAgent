from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from pydantic import BaseModel
from routers import auth, agents, chat, tags

app = FastAPI()

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

app.include_router(auth.router)
app.include_router(agents.router)
app.include_router(chat.router)
app.include_router(tags.router)


@app.get("/")
def read_root():
    return {"message": "Backend is running!"}


@app.post("/api/v1/chat/mock")
async def chat_mock(request: dict):
    return {
        "response": "これはモックサーバーからの返信です。",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/v1/poc/call-ollama")
async def call_ollama_poc():
    return {"service": "ollama", "status": "mock_ok"}


@app.get("/api/v1/poc/call-comfyui")
async def call_comfyui_poc():
    return {"service": "comfyui", "status": "mock_ok"}
