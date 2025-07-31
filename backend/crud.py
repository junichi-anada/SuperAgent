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
        joinedload(models.Agent.tones)
    ).filter(models.Agent.owner_id == user_id).offset(skip).limit(limit).all()

def get_agent(db: Session, agent_id: int, user_id: int) -> Optional[models.Agent]:
    return db.query(models.Agent).options(
        joinedload(models.Agent.personalities),
        joinedload(models.Agent.roles),
        joinedload(models.Agent.tones)
    ).filter(models.Agent.id == agent_id, models.Agent.owner_id == user_id).first()

def update_agent(db: Session, agent_id: int, agent: schemas.AgentUpdate, user_id: int) -> Optional[models.Agent]:
    db_agent = db.query(models.Agent).filter(models.Agent.id == agent_id, models.Agent.owner_id == user_id).first()
    if db_agent:
        # Extract tag IDs
        personality_ids = agent.personality_ids
        role_ids = agent.role_ids
        tone_ids = agent.tone_ids
        
        # Update basic fields
        agent_data = agent.dict(exclude={'personality_ids', 'role_ids', 'tone_ids'}, exclude_unset=True)
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

def delete_agent(db: Session, agent_id: int, user_id: int) -> bool:
    db_agent = get_agent(db, agent_id, user_id)
    if db_agent:
        db.delete(db_agent)
        db.commit()
        return True
    return False

def create_chat(db: Session, chat: schemas.ChatCreate, user_id: int):
    db_chat = models.Chat(agent_id=chat.agent_id, user_id=user_id)
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat

def get_chat(db: Session, chat_id: int, user_id: int) -> Optional[models.Chat]:
    return db.query(models.Chat).filter(models.Chat.id == chat_id, models.Chat.user_id == user_id).first()

def get_chats_by_agent_id(db: Session, agent_id: int, user_id: int, skip: int = 0, limit: int = 100) -> List[models.Chat]:
    return db.query(models.Chat).filter(models.Chat.agent_id == agent_id, models.Chat.user_id == user_id).offset(skip).limit(limit).all()

def create_message(db: Session, message: schemas.MessageCreate, chat_id: int, sender: str, image_url: Optional[str] = None):
    db_message = models.Message(content=message.content, chat_id=chat_id, sender=sender, image_url=image_url)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_messages(db: Session, chat_id: int, skip: int = 0, limit: int = 100) -> List[models.Message]:
    return db.query(models.Message).filter(models.Message.chat_id == chat_id).offset(skip).limit(limit).all()

# Tag-related CRUD operations
def get_personalities(db: Session) -> List[models.Personality]:
    return db.query(models.Personality).all()

def get_roles(db: Session) -> List[models.Role]:
    return db.query(models.Role).all()

def get_tones(db: Session) -> List[models.Tone]:
    return db.query(models.Tone).all()
