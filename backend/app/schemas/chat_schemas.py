from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    sentiment: Optional[str] = None
    dominant_emotion: Optional[str] = None
    crisis_flag: Optional[bool] = None


class VoiceChatResponse(BaseModel):
    """Returned after processing a voice message."""
    transcription: str         # what the user said
    response: str              # therapist reply text
    sentiment: Optional[str] = None
    dominant_emotion: Optional[str] = None
    crisis_flag: Optional[bool] = None
    audio_url: Optional[str] = None  # URL to synthesised speech (if TTS enabled)


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
    created_at: datetime

    class Config:
        from_attributes = True
