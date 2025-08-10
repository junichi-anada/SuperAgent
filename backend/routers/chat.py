from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from datetime import datetime
from sqlalchemy.orm import Session
from typing import List
import json
import httpx
import logging
import schemas, crud, models
from database import get_db
from auth import get_current_user, get_user_from_token
from services.llm_service import LLMService
from services.feedback_service import FeedbackService
from dependencies import get_llm_service, get_feedback_service, get_prompt_builder
from services.prompt_builder import PromptBuilder
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chats", tags=["chats"])

@router.post("/", response_model=schemas.ChatWithFirstMessages)
async def create_chat(
    chat: schemas.ChatCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
    llm_service: LLMService = Depends(get_llm_service)
):
    agent = crud.get_agent(db, chat.agent_id, current_user.id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    db_chat = crud.create_chat(db=db, chat=chat, user_id=current_user.id)
    
    messages = []
    if chat.first_message:
        # 1. Save user's first message
        user_message_schema = schemas.MessageCreate(content=chat.first_message)
        user_message = crud.create_message(db=db, message=user_message_schema, chat_id=db_chat.id, sender="user")
        messages.append(user_message)

        # 2. Get AI response
        try:
            response = await llm_service.generate_response(
                db=db,
                message=chat.first_message,
                agent=agent,
                chat_id=db_chat.id,
                user_message_id=user_message.id,
                websocket=None, # No websocket for the first message
            )
            
            ai_message_content = response.get("content", "...")
            image_url = response.get("image_url")

        except Exception as e:
            logger.error(f"Error generating first AI response for chat {db_chat.id}: {e}")
            ai_message_content = "申し訳ございません、最初の応答を生成できませんでした。"
            image_url = None

        # 3. Save AI's first message
        ai_message_schema = schemas.MessageCreate(content=ai_message_content)
        ai_message = crud.create_message(db=db, message=ai_message_schema, chat_id=db_chat.id, sender="ai", image_url=image_url)
        messages.append(ai_message)

    # Return chat with messages
    return schemas.ChatWithFirstMessages(
        id=db_chat.id,
        user_id=db_chat.user_id,
        agent_id=db_chat.agent_id,
        created_at=db_chat.created_at,
        messages=messages
    )

@router.get("/{chat_id}", response_model=schemas.Chat)
def get_chat_details(chat_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    chat = crud.get_chat(db, chat_id, current_user.id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat

@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat(chat_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    success = crud.delete_chat(db, chat_id=chat_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Chat not found")
    return

@router.get("/agent/{agent_id}", response_model=List[schemas.Chat])
def get_chats_by_agent(agent_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    chats = crud.get_chats_by_agent_id(db, agent_id=agent_id, user_id=current_user.id, skip=skip, limit=limit)
    return chats

@router.get("/{chat_id}/messages", response_model=List[schemas.Message])
def get_messages(chat_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    chat = crud.get_chat(db, chat_id, current_user.id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    return crud.get_messages(db=db, chat_id=chat_id, skip=skip, limit=limit)

@router.post("/{chat_id}/messages", response_model=List[schemas.Message])
async def send_message(
    chat_id: int,
    message: schemas.MessageCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
    llm_service: LLMService = Depends(get_llm_service),
    feedback_service: FeedbackService = Depends(get_feedback_service),
    prompt_builder: PromptBuilder = Depends(get_prompt_builder)
):
    chat = crud.get_chat(db, chat_id, current_user.id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # Create user message
    user_message = crud.create_message(db=db, message=message, chat_id=chat_id, sender="user")

    # --- Special command handling ---
    if message.content == "システムプロンプト見せて":
        # Re-fetch the agent directly to ensure all fields are up-to-date
        latest_agent = crud.get_agent(db, agent_id=chat.agent_id, user_id=current_user.id)
        if not latest_agent:
            raise HTTPException(status_code=404, detail="Agent not found when fetching for prompt")

        # Fetch conversation history to include in the prompt display
        db_messages = crud.get_messages(db, chat_id=chat_id, skip=0, limit=5)
        context = [
            {"sender": msg.sender, "content": msg.content}
            for msg in reversed(db_messages)
        ]
        system_prompt = await prompt_builder.build(
            agent=latest_agent,
            message="",
            context=context
        )
        ai_message_content = f"【システムプロンプト】\n```\n{system_prompt}\n```"
        ai_message_schema = schemas.MessageCreate(content=ai_message_content)
        ai_message = crud.create_message(db=db, message=ai_message_schema, chat_id=chat_id, sender="ai")
        return [user_message, ai_message]

    # --- Second Person Feedback Extraction ---
    # Get the agent associated with the chat
    agent = crud.get_agent(db, agent_id=chat.agent_id, user_id=current_user.id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent for this chat not found")

    # --- Second Person Feedback Extraction ---
    extracted_second_person = await feedback_service.extract_second_person(message.content)
    if extracted_second_person:
        agent_update = schemas.AgentUpdate(second_person=extracted_second_person)
        # Update the agent and get the updated object back
        agent = crud.update_agent(db=db, agent_id=chat.agent_id, agent=agent_update, user_id=current_user.id)
    # --- End of Feedback Extraction ---
    
    try:
        # Get AI response using LLM service, passing the agent object directly
        response = await llm_service.generate_response(
            db=db,
            message=message.content,
            agent=agent,
            chat_id=chat_id,
        )
        
        if response.get("error"):
            # If there's an error, still create an AI message with the error content
            ai_message_schema = schemas.MessageCreate(content=response["content"])
            ai_message = crud.create_message(db=db, message=ai_message_schema, chat_id=chat_id, sender="ai")
        else:
            ai_message_schema = schemas.MessageCreate(content=response["content"])
            # 画像URLがある場合は含める
            image_url = response.get("image_url")
            ai_message = crud.create_message(
                db=db,
                message=ai_message_schema,
                chat_id=chat_id,
                sender="ai",
                image_url=image_url
            )
        
    except Exception as e:
        # Create an error message as AI response
        error_content = "申し訳ございません、応答の生成中にエラーが発生しました。"
        ai_message_schema = schemas.MessageCreate(content=error_content)
        ai_message = crud.create_message(db=db, message=ai_message_schema, chat_id=chat_id, sender="ai")
    
    return [user_message, ai_message]

@router.websocket("/ws/{chat_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    chat_id: int,
    db: Session = Depends(get_db),
    llm_service: LLMService = Depends(get_llm_service),
    feedback_service: FeedbackService = Depends(get_feedback_service),
    prompt_builder: PromptBuilder = Depends(get_prompt_builder)
):
    logger.info(f"WebSocket connection attempt for chat_id: {chat_id}")
    
    # トークンベースの認証を有効化
    token = websocket.query_params.get("token")
    if not token:
        logger.warning(f"WebSocket connection for chat {chat_id} failed: No token provided.")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    logger.info(f"Token received for chat {chat_id}")
    user = get_user_from_token(db, token)
    if not user:
        logger.warning(f"WebSocket connection for chat {chat_id} failed: Invalid token.")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    logger.info(f"User {user.email} authenticated for chat {chat_id}")
    chat = crud.get_chat(db, chat_id, user.id)
    if not chat:
        logger.warning(f"WebSocket connection for chat {chat_id} failed: Chat not found for user {user.email}.")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()
    logger.info(f"WebSocket connection accepted for chat {chat_id} with user {user.email}")
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # --- Special command handling ---
            if message_data["content"] == "システムプロンプト見せて":
                # Re-fetch the agent directly to ensure all fields are up-to-date
                latest_agent = crud.get_agent(db, agent_id=chat.agent_id, user_id=user.id)
                if not latest_agent:
                    # This should ideally not happen if the initial check passed
                    await websocket.send_json({"error": True, "content": "Agent not found."})
                    continue

                # Build the prompt
                # Fetch conversation history to include in the prompt display
                db_messages = crud.get_messages(db, chat_id=chat_id, skip=0, limit=5)
                context = [
                    {"sender": msg.sender, "content": msg.content}
                    for msg in reversed(db_messages)
                ]
                system_prompt = await prompt_builder.build(
                    agent=latest_agent,
                    message="",
                    context=context
                )
                
                # Send the prompt as an AI message
                await websocket.send_json({
                    "id": f"system_prompt_{chat_id}",
                    "content": f"【システムプロンプト】\n```\n{system_prompt}\n```",
                    "sender": "ai",
                    "image_url": None,
                    "timestamp": datetime.utcnow().isoformat(),
                    "metadata": {"type": "system_prompt"}
                })
                continue # Skip the rest of the loop

            # Create user message
            user_message = schemas.MessageCreate(content=message_data["content"])
            saved_user_message = crud.create_message(db=db, message=user_message, chat_id=chat_id, sender="user")

            # Get the agent associated with the chat
            agent = crud.get_agent(db, agent_id=chat.agent_id, user_id=user.id)
            if not agent:
                await websocket.send_json({"error": True, "content": "Agent for this chat not found"})
                continue

            # --- Second Person Feedback Extraction ---
            extracted_second_person = await feedback_service.extract_second_person(saved_user_message.content)
            if extracted_second_person:
                agent_update = schemas.AgentUpdate(second_person=extracted_second_person)
                # Update the agent and get the updated object back
                agent = crud.update_agent(db=db, agent_id=chat.agent_id, agent=agent_update, user_id=user.id)
            # --- End of Feedback Extraction ---

            # Send user message back to client
            await websocket.send_json({
                "id": saved_user_message.id,
                "content": saved_user_message.content,
                "sender": saved_user_message.sender,
                "image_url": saved_user_message.image_url,
                "timestamp": saved_user_message.created_at.isoformat()
            })
            
            # Send "thinking" status
            try:
                await websocket.send_json({
                    "type": "status",
                    "status": "thinking",
                    "message": "考え中..."
                })
            except Exception as e:
                logger.error(f"Failed to send thinking status: {e}")

            # Get AI response
            try:
                response = await llm_service.generate_response(
                    db=db,
                    message=message_data["content"],
                    agent=agent,
                    chat_id=chat_id,
                    user_message_id=saved_user_message.id,
                    websocket=websocket, # Pass websocket object
                )

                if response.get("error"):
                    # エラーレスポンスの構造を統一
                    error_response = {
                        "id": f"error_{chat_id}_{datetime.utcnow().timestamp()}",
                        "content": response.get("content", "エラーが発生しました"),
                        "sender": "system",
                        "image_url": None,
                        "timestamp": datetime.utcnow().isoformat(),
                        "error": True,
                        "error_type": response.get("error_type", "unknown")
                    }
                    await websocket.send_json(error_response)
                    logger.error(f"LLM service returned error: {response}")
                    continue

                # Save AI message with image URL if present
                ai_message = schemas.MessageCreate(content=response["content"])
                image_url = response.get("image_url")
                saved_ai_message = crud.create_message(
                    db=db,
                    message=ai_message,
                    chat_id=chat_id,
                    sender="ai",
                    image_url=image_url
                )
                
                # Send AI message to client
                await websocket.send_json({
                    "id": saved_ai_message.id,
                    "content": saved_ai_message.content,
                    "sender": saved_ai_message.sender,
                    "image_url": saved_ai_message.image_url,
                    "timestamp": saved_ai_message.created_at.isoformat(),
                    "metadata": response.get("metadata", {})
                })
                
            except Exception as e:
                # This is a fallback for unexpected errors within the router itself.
                # The LLMService errors are already handled.
                logger.error(f"Unexpected error in WebSocket handler: {e}", exc_info=True)
                error_response = {
                    "id": f"error_{chat_id}_{datetime.utcnow().timestamp()}",
                    "content": "申し訳ございません、予期せぬエラーが発生しました。",
                    "sender": "system",
                    "image_url": None,
                    "timestamp": datetime.utcnow().isoformat(),
                    "error": True,
                    "error_type": "system_error"
                }
                try:
                    await websocket.send_json(error_response)
                except Exception as send_error:
                    logger.error(f"Failed to send error response: {send_error}")
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for chat {chat_id}")
    except Exception as e:
        logger.error(f"Unexpected error in WebSocket for chat {chat_id}: {e}", exc_info=True)
