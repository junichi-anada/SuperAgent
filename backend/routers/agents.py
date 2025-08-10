import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import shutil
import uuid
from pathlib import Path

import crud
import schemas
from database import get_db
from auth import oauth2_scheme
from jose import JWTError, jwt
from auth import SECRET_KEY, ALGORITHM
from services.image_generation_service import ImageGenerationService

router = APIRouter(
    prefix="/agents",
    tags=["agents"]
)

def get_image_generation_service(request: Request) -> ImageGenerationService:
    return request.app.state.image_generation_service

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user

@router.post("/", response_model=schemas.Agent)
def create_agent(
    agent: schemas.AgentCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    return crud.create_agent(db=db, agent=agent, user_id=current_user.id)

@router.get("/", response_model=List[schemas.Agent])
def read_agents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    agents = crud.get_agents(db, user_id=current_user.id, skip=skip, limit=limit)
    return agents

@router.get("/{agent_id}", response_model=schemas.Agent)
def read_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    db_agent = crud.get_agent(db, agent_id=agent_id, user_id=current_user.id)
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return db_agent

@router.put("/{agent_id}", response_model=schemas.Agent)
def update_agent(
    agent_id: int,
    agent: schemas.AgentUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    db_agent = crud.update_agent(db, agent_id=agent_id, agent=agent, user_id=current_user.id)
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return db_agent

@router.delete("/{agent_id}")
def delete_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    success = crud.delete_agent(db, agent_id=agent_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"detail": "Agent deleted"}


@router.delete("/{agent_id}/image")
def delete_agent_image(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
    image_service: ImageGenerationService = Depends(get_image_generation_service)
):
    """エージェントの画像を削除します。
    
    Args:
        agent_id: エージェントID
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Starting image deletion for agent {agent_id}")
    
    try:
        # エージェントの存在確認
        agent = crud.get_agent(db, agent_id=agent_id, user_id=current_user.id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        updated_agent, image_url_to_delete = crud.delete_primary_agent_image(db, agent_id=agent_id, user_id=current_user.id)

        if not updated_agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        if image_url_to_delete:
            image_service._remove_old_image(image_url_to_delete)
        
        logger.info(f"Successfully deleted primary image for agent {agent_id}")
        return {"detail": "Image deleted successfully"}
        
    except HTTPException:
        logger.error(f"HTTPException during image deletion for agent {agent_id}")
        raise
    except Exception as e:
        import traceback
        logger.error(f"Unexpected error during image deletion for agent {agent_id}: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"予期しないエラーが発生しました: {str(e)}")


@router.post("/{agent_id}/generate-image")
async def generate_agent_image(
    agent_id: int,
    request: schemas.ImageGenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
    image_service: ImageGenerationService = Depends(get_image_generation_service)
):
    """エージェントの外見画像をバックグラウンドで生成します。"""
    logger = logging.getLogger(__name__)
    logger.info(f"Received image generation request for agent {agent_id}, force_regenerate: {request.force_regenerate}")

    # エージェントの存在確認
    agent = crud.get_agent(db, agent_id=agent_id, user_id=current_user.id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # 画像生成をバックグラウンドタスクとして追加
    background_tasks.add_task(
        image_service.generate_and_save_image,
        agent_id=agent_id,
        user_id=current_user.id,
        force_regenerate=request.force_regenerate
    )
    
    logger.info(f"Image generation task for agent {agent_id} has been added to background tasks.")
    
    return {"message": "Image generation started in the background."}


@router.get("/{agent_id}/generation-log")
def get_generation_log(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
    image_service: ImageGenerationService = Depends(get_image_generation_service)
):
    """エージェントの画像生成ログを取得します。
    
    Args:
        agent_id: エージェントID
    
    Returns:
        生成ログの詳細情報
    """
    # エージェントの存在確認
    agent = crud.get_agent(db, agent_id=agent_id, user_id=current_user.id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # 画像生成サービスからログを取得
    generation_log = image_service.get_generation_log(agent_id)
    
    if not generation_log:
        return {
            "message": "No generation log found for this agent",
            "agent_id": agent_id
        }
    
    return generation_log


# Agent Images (Photo Gallery) endpoints
@router.get("/{agent_id}/images", response_model=List[schemas.AgentImage])
def get_agent_images(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """エージェントの画像リストを取得します。"""
    # エージェントの存在確認
    agent = crud.get_agent(db, agent_id=agent_id, user_id=current_user.id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    images = crud.get_agent_images(db, agent_id=agent_id)
    return images


@router.post("/{agent_id}/images", response_model=schemas.AgentImage)
async def upload_agent_image(
    agent_id: int,
    file: UploadFile = File(...),
    is_primary: bool = False,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
    image_service: ImageGenerationService = Depends(get_image_generation_service)
):
    """エージェントに新しい画像をアップロードします。"""
    logger = logging.getLogger(__name__)
    
    # エージェントの存在確認
    agent = crud.get_agent(db, agent_id=agent_id, user_id=current_user.id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # ファイル検証
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only images are allowed.")
    
    # ファイル保存
    try:
        # ユニークなファイル名を生成
        file_extension = Path(file.filename).suffix
        unique_filename = f"agent_{agent_id}_{uuid.uuid4()}{file_extension}"
        file_path = image_service.storage_path / unique_filename
        
        # ファイルを保存
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # URLを生成
        image_url = f"/static/agent_images/{unique_filename}"
        
        # データベースに保存
        db_image = crud.create_agent_image(db, agent_id=agent_id, image_url=image_url, is_primary=is_primary)
        
        logger.info(f"Successfully uploaded image for agent {agent_id}: {image_url}")
        return db_image
        
    except Exception as e:
        logger.error(f"Error uploading image for agent {agent_id}: {str(e)}")
        # クリーンアップ
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")


@router.delete("/{agent_id}/images/{image_id}")
def delete_agent_gallery_image(
    agent_id: int,
    image_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
    image_service: ImageGenerationService = Depends(get_image_generation_service)
):
    """エージェントのギャラリー画像を削除します。"""
    logger = logging.getLogger(__name__)
    
    # エージェントの存在確認
    agent = crud.get_agent(db, agent_id=agent_id, user_id=current_user.id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # 画像を取得
    images = crud.get_agent_images(db, agent_id=agent_id)
    image_to_delete = next((img for img in images if img.id == image_id), None)
    
    if not image_to_delete:
        raise HTTPException(status_code=404, detail="Image not found")
    
    try:
        # 物理ファイルを削除
        if image_to_delete.image_url:
            image_service._remove_old_image(image_to_delete.image_url)
        
        # データベースから削除
        success = crud.delete_agent_gallery_image(db, agent_id=agent_id, image_id=image_id)
        if not success:
            raise HTTPException(status_code=404, detail="Image not found")
        
        logger.info(f"Successfully deleted image {image_id} for agent {agent_id}")
        return {"detail": "Image deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting image {image_id} for agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete image: {str(e)}")


@router.put("/{agent_id}/images/{image_id}/set-primary", response_model=schemas.AgentImage)
def set_primary_image(
    agent_id: int,
    image_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """指定した画像をプライマリ画像に設定します。"""
    # エージェントの存在確認
    agent = crud.get_agent(db, agent_id=agent_id, user_id=current_user.id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # プライマリ画像を設定
    db_image = crud.set_primary_agent_image(db, agent_id=agent_id, image_id=image_id)
    if not db_image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    return db_image
