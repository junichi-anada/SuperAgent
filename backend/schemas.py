from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserBase(BaseModel):
    username: str
    email: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

class TagBase(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class Personality(TagBase):
    pass

class Role(TagBase):
    pass

class Tone(TagBase):
    pass

class AgentBase(BaseModel):
    name: str
    description: Optional[str] = None
    gender: Optional[str] = None
    background: Optional[str] = None

class AgentCreate(AgentBase):
    personality_ids: List[int] = []
    role_ids: List[int] = []
    tone_ids: List[int] = []

class AgentUpdate(AgentBase):
    name: Optional[str] = None
    personality_ids: List[int] = []
    role_ids: List[int] = []
    tone_ids: List[int] = []

class Agent(AgentBase):
    id: int
    created_at: datetime
    owner_id: int
    personalities: List[Personality] = []
    roles: List[Role] = []
    tones: List[Tone] = []

    class Config:
        orm_mode = True

class ChatBase(BaseModel):
    pass

class ChatCreate(ChatBase):
    agent_id: int

class Chat(ChatBase):
    id: int
    user_id: int
    agent_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class MessageBase(BaseModel):
    content: str

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: int
    chat_id: int
    sender: str
    image_url: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True
