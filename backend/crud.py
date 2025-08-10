from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import models, schemas
from auth import get_password_hash

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_agent(db: Session, agent: schemas.AgentCreate, user_id: int):
    # Extract tag IDs before creating agent
    personality_ids = agent.personality_ids
    role_ids = agent.role_ids
    tone_ids = agent.tone_ids
    
    # Create agent without tag IDs
    agent_data = agent.dict()
    agent_data.pop('personality_ids', None)
    agent_data.pop('role_ids', None)
    agent_data.pop('tone_ids', None)
    
    db_agent = models.Agent(**agent_data, owner_id=user_id)
    db.add(db_agent)
    db.flush()  # Flush to get ID but don't commit yet
    
    # Add relationships
    if personality_ids:
        personalities = db.query(models.Personality).filter(models.Personality.id.in_(personality_ids)).all()
        db_agent.personalities = personalities
    
    if role_ids:
        roles = db.query(models.Role).filter(models.Role.id.in_(role_ids)).all()
        db_agent.roles = roles
    
    if tone_ids:
        tones = db.query(models.Tone).filter(models.Tone.id.in_(tone_ids)).all()
        db_agent.tones = tones
    
    db.commit()
    db.refresh(db_agent)
    return db_agent

def get_agents(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[models.Agent]:
    return db.query(models.Agent).options(
        joinedload(models.Agent.personalities),
        joinedload(models.Agent.roles),
        joinedload(models.Agent.tones),
        joinedload(models.Agent.images)
    ).filter(models.Agent.owner_id == user_id).offset(skip).limit(limit).all()

def get_agent(db: Session, agent_id: int, user_id: int) -> Optional[models.Agent]:
    return db.query(models.Agent).options(
        joinedload(models.Agent.personalities),
        joinedload(models.Agent.roles),
        joinedload(models.Agent.tones),
        joinedload(models.Agent.images)
    ).filter(models.Agent.id == agent_id, models.Agent.owner_id == user_id).first()

def get_agent_without_user_check(db: Session, agent_id: int) -> Optional[models.Agent]:
    """Get an agent without user_id check (for testing purposes only)"""
    return db.query(models.Agent).options(
        joinedload(models.Agent.personalities),
        joinedload(models.Agent.roles),
        joinedload(models.Agent.tones),
        joinedload(models.Agent.images)
    ).filter(models.Agent.id == agent_id).first()

def update_agent(db: Session, agent_id: int, agent: schemas.AgentUpdate, user_id: int) -> Optional[models.Agent]:
    db_agent = db.query(models.Agent).filter(models.Agent.id == agent_id, models.Agent.owner_id == user_id).first()
    if db_agent:
        # Extract tag IDs
        personality_ids = agent.personality_ids
        role_ids = agent.role_ids
        tone_ids = agent.tone_ids
        
        # Update basic fields
        agent_data = agent.dict(exclude={'personality_ids', 'role_ids', 'tone_ids'}, exclude_unset=True)
        
        # Special handling for image_seed field
        # If image_seed is explicitly provided (even as None), we should update it
        if 'image_seed' in agent.dict(exclude_unset=False):
            agent_data['image_seed'] = agent.image_seed
        
        for key, value in agent_data.items():
            setattr(db_agent, key, value)
        
        # Update relationships
        if personality_ids is not None:
            personalities = db.query(models.Personality).filter(models.Personality.id.in_(personality_ids)).all() if personality_ids else []
            db_agent.personalities = personalities
        
        if role_ids is not None:
            roles = db.query(models.Role).filter(models.Role.id.in_(role_ids)).all() if role_ids else []
            db_agent.roles = roles
        
        if tone_ids is not None:
            tones = db.query(models.Tone).filter(models.Tone.id.in_(tone_ids)).all() if tone_ids else []
            db_agent.tones = tones
        
        db.commit()
        db.refresh(db_agent)
    return db_agent


def update_agent_image_details(db: Session, agent_id: int, image_url: str, image_seed: int) -> Optional[models.Agent]:
    """エージェントの画像URLとシード値を更新します。"""
    db_agent = db.query(models.Agent).filter(models.Agent.id == agent_id).first()
    if db_agent:
        db_agent.image_url = image_url
        db_agent.image_seed = image_seed
        db.commit()
        db.refresh(db_agent)
    return db_agent

def delete_primary_agent_image(db: Session, agent_id: int, user_id: int):
    """エージェントのプライマリ画像を削除し、関連する agent_images エントリも削除します。"""
    agent = db.query(models.Agent).filter(models.Agent.id == agent_id, models.Agent.owner_id == user_id).first()
    if not agent:
        return None, None

    image_url_to_delete = agent.image_url

    # agent_images テーブルからプライマリ画像を削除
    primary_image = db.query(models.AgentImage).filter(
        models.AgentImage.agent_id == agent_id,
        models.AgentImage.is_primary == True
    ).first()

    if primary_image:
        db.delete(primary_image)

    # agents テーブルの画像情報をクリア
    agent.image_url = None
    agent.image_seed = None
    
    db.commit()
    db.refresh(agent)
    
    return agent, image_url_to_delete

# Agent Images CRUD operations
def create_agent_image(db: Session, agent_id: int, image_url: str, is_primary: bool = False, image_seed: Optional[int] = None):
    # If setting as primary, unset other primary images first
    if is_primary:
        db.query(models.AgentImage).filter(
            models.AgentImage.agent_id == agent_id,
            models.AgentImage.is_primary == True
        ).update({models.AgentImage.is_primary: False})
        
        # Also update the agent's main image_url and seed
        agent = db.query(models.Agent).filter(models.Agent.id == agent_id).first()
        if agent:
            agent.image_url = image_url
            if image_seed is not None:
                agent.image_seed = image_seed
    
    db_image = models.AgentImage(
        agent_id=agent_id,
        image_url=image_url,
        is_primary=is_primary
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

def get_agent_images(db: Session, agent_id: int):
    return db.query(models.AgentImage).filter(
        models.AgentImage.agent_id == agent_id
    ).order_by(models.AgentImage.is_primary.desc(), models.AgentImage.created_at.desc()).all()

def delete_agent_gallery_image(db: Session, agent_id: int, image_id: int):
    db_image = db.query(models.AgentImage).filter(
        models.AgentImage.id == image_id,
        models.AgentImage.agent_id == agent_id
    ).first()
    
    if db_image:
        # If deleting primary image, update agent's image_url to None
        if db_image.is_primary:
            agent = db.query(models.Agent).filter(models.Agent.id == agent_id).first()
            if agent:
                agent.image_url = None
                agent.image_seed = None
        
        db.delete(db_image)
        db.commit()
        return True
    return False

def set_primary_agent_image(db: Session, agent_id: int, image_id: int):
    # Get the image to set as primary
    db_image = db.query(models.AgentImage).filter(
        models.AgentImage.id == image_id,
        models.AgentImage.agent_id == agent_id
    ).first()
    
    if not db_image:
        return None
    
    # Unset all other primary images for this agent
    db.query(models.AgentImage).filter(
        models.AgentImage.agent_id == agent_id,
        models.AgentImage.is_primary == True
    ).update({models.AgentImage.is_primary: False})
    
    # Set this image as primary
    db_image.is_primary = True
    
    # Update agent's main image_url
    agent = db.query(models.Agent).filter(models.Agent.id == agent_id).first()
    if agent:
        agent.image_url = db_image.image_url
    
    db.commit()
    db.refresh(db_image)
    return db_image

def delete_agent(db: Session, agent_id: int, user_id: int) -> bool:
    db_agent = get_agent(db, agent_id, user_id)
    if db_agent:
        db.delete(db_agent)
        db.commit()
        return True
    return False

def create_chat(db: Session, chat: schemas.ChatCreate, user_id: int):
    """
    新しいチャットを作成します。
    もし first_message が提供されていれば、それも処理します。
    """
    db_chat = models.Chat(agent_id=chat.agent_id, user_id=user_id)
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    
    # first_message があれば、ここで保存するロジックは router 側に移動
    # なぜなら、LLMサービスの呼び出しなど、ビジネスロジックが関わるため
    
    return db_chat

def get_chat(db: Session, chat_id: int, user_id: int) -> Optional[models.Chat]:
    return db.query(models.Chat).filter(models.Chat.id == chat_id, models.Chat.user_id == user_id).first()

def get_chats_by_agent_id(db: Session, agent_id: int, user_id: int, skip: int = 0, limit: int = 100) -> List[models.Chat]:
    return db.query(models.Chat).filter(models.Chat.agent_id == agent_id, models.Chat.user_id == user_id).offset(skip).limit(limit).all()

def delete_chat(db: Session, chat_id: int, user_id: int) -> bool:
    db_chat = get_chat(db, chat_id, user_id)
    if db_chat:
        db.delete(db_chat)
        db.commit()
        return True
    return False

def create_message(db: Session, message: schemas.MessageCreate, chat_id: int, sender: str, image_url: Optional[str] = None):
    db_message = models.Message(content=message.content, chat_id=chat_id, sender=sender, image_url=image_url)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_messages(db: Session, chat_id: int, skip: int = 0, limit: int = 100) -> List[models.Message]:
    return db.query(models.Message).filter(models.Message.chat_id == chat_id).offset(skip).limit(limit).all()
def get_message(db: Session, message_id: int) -> Optional[models.Message]:
    return db.query(models.Message).filter(models.Message.id == message_id).first()

# Tag-related CRUD operations
def get_personalities(db: Session) -> List[models.Personality]:
    return db.query(models.Personality).all()

def get_roles(db: Session) -> List[models.Role]:
    return db.query(models.Role).all()

def get_tones(db: Session) -> List[models.Tone]:
    return db.query(models.Tone).all()


def create_image_generation_log(db: Session, log: schemas.ImageGenerationLogCreate):
    db_log = models.ImageGenerationLog(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log