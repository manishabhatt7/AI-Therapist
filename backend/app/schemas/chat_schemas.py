
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class ChatRequest(BaseModel):
    message: str


class ChatSessionCreate(BaseModel):
    pass  # No fields needed for creation

class ChatSessionOut(BaseModel):
    id: str
    user_id: str
    created_at: datetime

class ChatMessageOut(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime

class ChatResponse(BaseModel):
    response: str

    