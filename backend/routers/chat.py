from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session
from typing import List
import httpx
import json
import schemas, crud
from database import get_db
from auth import get_current_user, get_user_from_token

router = APIRouter(prefix="/chats", tags=["chats"])

@router.post("/", response_model=schemas.Chat)
def create_chat(chat: schemas.ChatCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    agent = crud.get_agent(db, chat.agent_id, current_user.id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return crud.create_chat(db=db, chat=chat, user_id=current_user.id)

@router.get("/{chat_id}", response_model=schemas.Chat)
def get_chat_details(chat_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    chat = crud.get_chat(db, chat_id, current_user.id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat

@router.get("/{chat_id}/messages", response_model=List[schemas.Message])
def get_messages(chat_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    chat = crud.get_chat(db, chat_id, current_user.id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    return crud.get_messages(db=db, chat_id=chat_id, skip=skip, limit=limit)

@router.post("/{chat_id}/messages", response_model=schemas.Message)
def send_message(chat_id: int, message: schemas.MessageCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    chat = crud.get_chat(db, chat_id, current_user.id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    user_message = crud.create_message(db=db, message=message, chat_id=chat_id, sender="user")
    
    try:
        # This is a synchronous endpoint, so we can use httpx.post directly.
        # For async endpoints, you would use `async with httpx.AsyncClient() as client:`
        with httpx.Client() as client:
            response = client.post("http://localhost:8000/api/v1/chat/mock", json={"message": message.content})
            response.raise_for_status()
            ai_response = response.json()["response"]
        
        ai_message = schemas.MessageCreate(content=ai_response)
        crud.create_message(db=db, message=ai_message, chat_id=chat_id, sender="ai")
        
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Failed to get AI response: {str(e)}")
    
    return user_message

@router.websocket("/ws/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: int, db: Session = Depends(get_db)):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    user = get_user_from_token(db, token)
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    chat = crud.get_chat(db, chat_id, user.id)
    if not chat:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # Validate token in message if exists
            if "token" in message_data:
                msg_user = get_user_from_token(db, message_data["token"])
                if not msg_user or msg_user.id != user.id:
                    await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                    continue

            # Create user message
            user_message = schemas.MessageCreate(content=message_data["content"])
            saved_user_message = crud.create_message(db=db, message=user_message, chat_id=chat_id, sender="user")

            # Send user message back to client
            await websocket.send_json({
                "id": saved_user_message.id,
                "content": saved_user_message.content,
                "sender": saved_user_message.sender,
                "image_url": saved_user_message.image_url,
                "timestamp": saved_user_message.created_at.isoformat()
            })
            
            # Get AI response (mock)
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post("http://localhost:8000/api/v1/chat/mock", json={"message": message_data["content"]})
                    response.raise_for_status()
                    ai_response = response.json()["response"]
                
                # Save AI message with mock image URL
                ai_message = schemas.MessageCreate(content=ai_response)
                saved_ai_message = crud.create_message(db=db, message=ai_message, chat_id=chat_id, sender="ai", image_url="https://via.placeholder.com/300")
                
                # Send AI message to client
                await websocket.send_json({
                    "id": saved_ai_message.id,
                    "content": saved_ai_message.content,
                    "sender": saved_ai_message.sender,
                    "image_url": saved_ai_message.image_url,
                    "timestamp": saved_ai_message.created_at.isoformat()
                })
                
            except httpx.RequestError as e:
                await websocket.send_json({
                    "error": f"Failed to get AI response: {str(e)}"
                })
                
    except WebSocketDisconnect:
        pass
