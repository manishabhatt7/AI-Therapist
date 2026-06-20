"""
chat_routes.py  –  Phase 1 + Phase 2
Adds:
  POST /chat/sessions/{session_id}/voice  – upload audio, get transcription + response
  GET  /chat/sessions/{session_id}/sentiment-summary  – emotion analytics for a session
"""
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.auth.auth_dependency import get_current_user
from app.database.database import get_db
from app.database.models import ChatMessage, ChatSession
from app.modules.llm_service import generate_response
from app.modules.sentiment_service import analyse_sentiment
from app.modules.voice_service import transcribe_audio
from app.schemas.chat_schemas import (
    ChatRequest, ChatResponse, VoiceChatResponse,
    ChatSessionCreate, ChatSessionOut, ChatMessageOut
)

router = APIRouter(tags=["Chat"], prefix="/chat")


# ────────────────────────────────────────────────────────────
#  Session management (unchanged from Phase 1)
# ────────────────────────────────────────────────────────────

@router.post("/sessions", response_model=ChatSessionOut)
def create_session(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = ChatSession(user_id=user_id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/sessions", response_model=List[ChatSessionOut])
def list_sessions(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user_id)
        .order_by(ChatSession.created_at.desc())
        .all()
    )


# ────────────────────────────────────────────────────────────
#  Phase 1: Text chat
# ────────────────────────────────────────────────────────────

@router.post("/sessions/{session_id}/message", response_model=ChatResponse)
def chat_in_session(
    session_id: str,
    request: ChatRequest,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a text message and receive a therapist response + sentiment analysis."""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == user_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Analyse sentiment before generating response
    sentiment_data = analyse_sentiment(request.message)

    ai_response = generate_response(
        session_id=session_id,
        user_message=request.message,
        db=db,
        sentiment_data=sentiment_data,
        input_type="text"
    )

    return ChatResponse(
        response=ai_response,
        sentiment=sentiment_data.get("sentiment"),
        dominant_emotion=sentiment_data.get("dominant_emotion"),
        crisis_flag=sentiment_data.get("crisis_flag")
    )


# ────────────────────────────────────────────────────────────
#  Phase 2: Voice chat
# ────────────────────────────────────────────────────────────

@router.post("/sessions/{session_id}/voice", response_model=VoiceChatResponse)
async def voice_chat_in_session(
    session_id: str,
    audio: UploadFile = File(..., description="Audio file (webm, mp3, wav, ogg, m4a)"),
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload audio → transcribe with Whisper → analyse sentiment → generate therapist response.

    Accepted audio formats: webm, mp3, wav, ogg, m4a
    Max recommended size: 25 MB (Groq/OpenAI API limit)
    """
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == user_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # 1. Read audio bytes
    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio file")

    # 2. Transcribe
    try:
        transcription = transcribe_audio(audio_bytes, filename=audio.filename or "audio.webm")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Transcription failed: {str(e)}")

    if not transcription.strip():
        raise HTTPException(status_code=422, detail="Could not transcribe audio – please speak clearly.")

    # 3. Sentiment analysis on transcribed text
    sentiment_data = analyse_sentiment(transcription)

    # 4. Generate therapist response
    ai_response = generate_response(
        session_id=session_id,
        user_message=transcription,
        db=db,
        sentiment_data=sentiment_data,
        input_type="voice",
        transcription=transcription
    )

    return VoiceChatResponse(
        transcription=transcription,
        response=ai_response,
        sentiment=sentiment_data.get("sentiment"),
        dominant_emotion=sentiment_data.get("dominant_emotion"),
        crisis_flag=sentiment_data.get("crisis_flag")
    )


# ────────────────────────────────────────────────────────────
#  Phase 2: Sentiment analytics for a session
# ────────────────────────────────────────────────────────────

@router.get("/sessions/{session_id}/sentiment-summary")
def get_sentiment_summary(
    session_id: str,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns aggregated emotion data for a session.
    Useful for therapist dashboard / user self-reflection views.
    """
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == user_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    user_messages = (
        db.query(ChatMessage)
        .filter(
            ChatMessage.session_id == session_id,
            ChatMessage.role == "user",
            ChatMessage.sentiment.isnot(None)
        )
        .all()
    )

    if not user_messages:
        return {"message": "No sentiment data available yet."}

    # Aggregate
    emotion_counts: dict = {}
    sentiment_counts: dict = {}
    scores = []
    crisis_count = 0

    for msg in user_messages:
        e = msg.dominant_emotion or "unknown"
        s = msg.sentiment or "neutral"
        emotion_counts[e] = emotion_counts.get(e, 0) + 1
        sentiment_counts[s] = sentiment_counts.get(s, 0) + 1
        if msg.sentiment_score:
            scores.append(msg.sentiment_score)

    dominant_emotion = max(emotion_counts, key=emotion_counts.get)
    avg_score = round(sum(scores) / len(scores), 2) if scores else None

    return {
        "session_id": session_id,
        "total_user_messages": len(user_messages),
        "dominant_emotion_overall": dominant_emotion,
        "emotion_breakdown": emotion_counts,
        "sentiment_breakdown": sentiment_counts,
        "average_confidence": avg_score,
        "voice_message_count": sum(1 for m in user_messages if m.input_type == "voice"),
        "text_message_count": sum(1 for m in user_messages if m.input_type == "text"),
    }


# ────────────────────────────────────────────────────────────
#  Message history
# ────────────────────────────────────────────────────────────

@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageOut])
def get_session_messages(
    session_id: str,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50
):
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == user_id
    ).first()
    if not session:
        return []

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .limit(limit)
        .all()
    )
    return [
        ChatMessageOut(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            input_type=msg.input_type,
            sentiment=msg.sentiment,
            dominant_emotion=msg.dominant_emotion,
            transcription=msg.transcription,
            created_at=msg.created_at
        )
        for msg in messages
    ]


@router.get("/history")
def get_chat_history(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50
):
    """Backward-compatible flat history endpoint."""
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == user_id)
        .order_by(ChatMessage.created_at.asc())
        .limit(limit)
        .all()
    )
    return {
        "messages": [
            {
                "role": msg.role,
                "content": msg.content,
                "input_type": msg.input_type,
                "sentiment": msg.sentiment,
                "dominant_emotion": msg.dominant_emotion,
                "created_at": msg.created_at,
            }
            for msg in messages
        ]
    }
