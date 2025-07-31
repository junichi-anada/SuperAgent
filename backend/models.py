from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, Text
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
    background = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    owner = relationship("User", back_populates="agents")
    chats = relationship("Chat", back_populates="agent")
    personalities = relationship("Personality", secondary=agent_personalities, back_populates="agents")
    roles = relationship("Role", secondary=agent_roles, back_populates="agents")
    tones = relationship("Tone", secondary=agent_tones, back_populates="agents")

class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    agent_id = Column(Integer, ForeignKey("agents.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="chats")
    agent = relationship("Agent", back_populates="chats")
    messages = relationship("Message", back_populates="chat")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"))
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
