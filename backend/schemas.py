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
        from_attributes = True

class TagBase(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

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
    relationship_status: Optional[str] = None
    background: Optional[str] = None
    hair_style: Optional[str] = None
    hair_color: Optional[str] = None
    eye_color: Optional[str] = None
    ethnicity: Optional[str] = None
    age: Optional[int] = None
    height: Optional[int] = None
    body_type: Optional[str] = None
    clothing: Optional[str] = None
    image_url: Optional[str] = None
    image_seed: Optional[int] = None
    first_person: Optional[str] = None
    first_person_other: Optional[str] = None
    second_person: Optional[str] = None

class AgentCreate(AgentBase):
    personality_ids: List[int] = []
    role_ids: List[int] = []
    tone_ids: List[int] = []

class AgentUpdate(AgentBase):
    name: Optional[str] = None
    relationship_status: Optional[str] = None
    background: Optional[str] = None
    hair_style: Optional[str] = None
    hair_color: Optional[str] = None
    eye_color: Optional[str] = None
    ethnicity: Optional[str] = None
    age: Optional[int] = None
    height: Optional[int] = None
    body_type: Optional[str] = None
    clothing: Optional[str] = None
    personality_ids: List[int] = []
    role_ids: List[int] = []
    tone_ids: List[int] = []
    image_url: Optional[str] = None
    image_seed: Optional[int] = None
    first_person: Optional[str] = None
    first_person_other: Optional[str] = None
    second_person: Optional[str] = None

class Agent(AgentBase):
    id: int
    created_at: datetime
    owner_id: int
    personalities: List[Personality] = []
    roles: List[Role] = []
    tones: List[Tone] = []
    images: List['AgentImage'] = []

    class Config:
        from_attributes = True

class ChatBase(BaseModel):
    pass

class ChatCreate(ChatBase):
    agent_id: int
    first_message: Optional[str] = None

class Chat(ChatBase):
    id: int
    user_id: int
    agent_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ChatWithFirstMessages(Chat):
    messages: List['Message'] = []

    class Config:
        from_attributes = True

class ImageGenerationRequest(BaseModel):
    force_regenerate: bool = False

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
        from_attributes = True

class AgentImageBase(BaseModel):
    image_url: str
    is_primary: bool = False

class AgentImageCreate(AgentImageBase):
    pass

class AgentImage(AgentImageBase):
    id: int
    agent_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Update forward references
Agent.model_rebuild()
ChatWithFirstMessages.model_rebuild()


class ImageGenerationLogBase(BaseModel):
    user_message: str
    keywords: Optional[str] = None
    model: Optional[str] = None
    prompt: str
    ip_adapter_model: Optional[str] = None
    image_url: str

class ImageGenerationLogCreate(ImageGenerationLogBase):
    agent_id: int
    message_id: Optional[int] = None

class ImageGenerationLog(ImageGenerationLogBase):
    id: int
    agent_id: int
    message_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True