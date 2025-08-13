from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, Text, Boolean, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

# Association tables for many-to-many relationships
agent_personalities = Table('agent_personalities', Base.metadata,
    Column('agent_id', Integer, ForeignKey('agents.id'), primary_key=True),
    Column('personality_id', Integer, ForeignKey('personalities.id'), primary_key=True)
)

agent_roles = Table('agent_roles', Base.metadata,
    Column('agent_id', Integer, ForeignKey('agents.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

agent_tones = Table('agent_tones', Base.metadata,
    Column('agent_id', Integer, ForeignKey('agents.id'), primary_key=True),
    Column('tone_id', Integer, ForeignKey('tones.id'), primary_key=True)
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    agents = relationship("Agent", back_populates="owner")
    chats = relationship("Chat", back_populates="user")

class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    gender = Column(String, nullable=True)
    relationship_status = Column(String, nullable=True)
    background = Column(Text, nullable=True)
    hair_style = Column(String, nullable=True)
    hair_color = Column(String, nullable=True)
    eye_color = Column(String, nullable=True)
    ethnicity = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    body_type = Column(String, nullable=True)
    clothing = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"))
    image_url = Column(String, nullable=True)
    image_seed = Column(BigInteger, nullable=True)
    first_person = Column(String, nullable=True)
    first_person_other = Column(String, nullable=True)
    second_person = Column(String, nullable=True)
    
    owner = relationship("User", back_populates="agents")
    chats = relationship("Chat", back_populates="agent")
    personalities = relationship("Personality", secondary=agent_personalities, back_populates="agents")
    roles = relationship("Role", secondary=agent_roles, back_populates="agents")
    tones = relationship("Tone", secondary=agent_tones, back_populates="agents")
    images = relationship("AgentImage", back_populates="agent", cascade="all, delete-orphan")

class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    agent_id = Column(Integer, ForeignKey("agents.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="chats")
    agent = relationship("Agent", back_populates="chats")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id", ondelete="CASCADE"))
    content = Column(String)
    sender = Column(String)  # "user" or "ai"
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    chat = relationship("Chat", back_populates="messages")

class Personality(Base):
    __tablename__ = "personalities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    
    agents = relationship("Agent", secondary=agent_personalities, back_populates="personalities")

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    
    agents = relationship("Agent", secondary=agent_roles, back_populates="roles")

class Tone(Base):
    __tablename__ = "tones"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    
    agents = relationship("Agent", secondary=agent_tones, back_populates="tones")

class AgentImage(Base):
    __tablename__ = "agent_images"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"))
    image_url = Column(String, nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    agent = relationship("Agent", back_populates="images")


class ImageGenerationLog(Base):
    __tablename__ = "image_generation_logs"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    user_message = Column(Text, nullable=False)
    keywords = Column(Text, nullable=True)
    model = Column(String, nullable=True)
    prompt = Column(Text, nullable=False)
    ip_adapter_model = Column(String, nullable=True)
    image_url = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    agent = relationship("Agent")
    message = relationship("Message")