from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    sentiment: Optional[str] = None
    dominant_emotion: Optional[str] = None
    crisis_flag: Optional[bool] = None
    audio_base64: Optional[str] = None
    audio_mime: Optional[str] = None   # "audio/wav" or "audio/mpeg"


class VoiceChatResponse(BaseModel):
    transcription: str
    response: str
    sentiment: Optional[str] = None
    dominant_emotion: Optional[str] = None
    crisis_flag: Optional[bool] = None
    audio_base64: Optional[str] = None
    audio_mime: Optional[str] = None


class ChatSessionCreate(BaseModel):
    pass


class ChatSessionOut(BaseModel):
    id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatMessageOut(BaseModel):
    id: str
    role: str
    content: str
    input_type: Optional[str] = "text"
    sentiment: Optional[str] = None
    dominant_emotion: Optional[str] = None
    transcription: Optional[str] = None
    crisis_flag: Optional[bool] = None
    created_at: datetime

    class Config:
        from_attributes = True