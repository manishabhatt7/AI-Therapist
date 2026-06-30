from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.auth.auth_dependency import get_current_user
from app.database.database import get_db
from app.database.models import ChatMessage, ChatSession
from app.modules.llm_service import generate_response
from app.modules.sentiment_service import analyse_sentiment
from app.modules.voice_service import transcribe_audio, synthesise_speech_base64
from app.config import settings
from app.schemas.chat_schemas import (
    ChatRequest, ChatResponse, VoiceChatResponse,
    ChatSessionOut, ChatMessageOut,
)

router = APIRouter(tags=["Chat"], prefix="/chat")


def _generate_audio(text: str) -> tuple:
    """Returns (base64_str, mime_type) or (None, None) on failure."""
    try:
        b64, mime = synthesise_speech_base64(text, voice=settings.tts_voice)
        return b64, mime
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"TTS failed: {e}")
        return None, None


# ── Sessions ──────────────────────────────────────────────────────

@router.post("/sessions", response_model=ChatSessionOut)
def create_session(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = ChatSession(user_id=user_id)
    db.add(session); db.commit(); db.refresh(session)
    return session


@router.get("/sessions", response_model=List[ChatSessionOut])
def list_sessions(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user_id)
        .order_by(ChatSession.created_at.desc())
        .all()
    )


# ── Text message ──────────────────────────────────────────────────

@router.post("/sessions/{session_id}/message", response_model=ChatResponse)
def send_message(
    session_id: str,
    request: ChatRequest,
    tts: bool = Query(default=True),
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id, ChatSession.user_id == user_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    sentiment_data = analyse_sentiment(request.message)
    ai_text = generate_response(
        session_id=session_id, user_message=request.message,
        db=db, sentiment_data=sentiment_data, input_type="text",
    )

    audio_base64, audio_mime = _generate_audio(ai_text) if tts else (None, None)

    return ChatResponse(
        response=ai_text,
        sentiment=sentiment_data.get("sentiment"),
        dominant_emotion=sentiment_data.get("dominant_emotion"),
        crisis_flag=sentiment_data.get("crisis_flag"),
        audio_base64=audio_base64,
        audio_mime=audio_mime,
    )


# ── Voice message ─────────────────────────────────────────────────

@router.post("/sessions/{session_id}/voice", response_model=VoiceChatResponse)
async def send_voice_message(
    session_id: str,
    audio: UploadFile = File(...),
    tts: bool = Query(default=True),
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id, ChatSession.user_id == user_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio file.")

    try:
        transcription = transcribe_audio(audio_bytes, filename=audio.filename or "audio.webm")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Transcription failed: {e}")

    if not transcription.strip():
        raise HTTPException(status_code=422, detail="Could not transcribe audio.")

    sentiment_data = analyse_sentiment(transcription)
    ai_text = generate_response(
        session_id=session_id, user_message=transcription,
        db=db, sentiment_data=sentiment_data,
        input_type="voice", transcription=transcription,
    )

    audio_base64, audio_mime = _generate_audio(ai_text) if tts else (None, None)

    return VoiceChatResponse(
        transcription=transcription,
        response=ai_text,
        sentiment=sentiment_data.get("sentiment"),
        dominant_emotion=sentiment_data.get("dominant_emotion"),
        crisis_flag=sentiment_data.get("crisis_flag"),
        audio_base64=audio_base64,
        audio_mime=audio_mime,
    )


# ── Messages ──────────────────────────────────────────────────────

@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageOut])
def get_messages(
    session_id: str,
    limit: int = 50,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id, ChatSession.user_id == user_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .limit(limit)
        .all()
    )
    return [
        ChatMessageOut(
            id=m.id, role=m.role, content=m.content,
            input_type=m.input_type, sentiment=m.sentiment,
            dominant_emotion=m.dominant_emotion, transcription=m.transcription,
            crisis_flag=m.crisis_flag, created_at=m.created_at,
        )
        for m in messages
    ]


# ── Sentiment summary ─────────────────────────────────────────────

@router.get("/sessions/{session_id}/sentiment-summary")
def get_sentiment_summary(
    session_id: str,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id, ChatSession.user_id == user_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    msgs = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id,
                ChatMessage.role == "user",
                ChatMessage.sentiment.isnot(None))
        .all()
    )
    if not msgs:
        return {"message": "No sentiment data yet."}

    emotion_counts, sentiment_counts, scores = {}, {}, []
    crisis_count = 0
    for m in msgs:
        e = m.dominant_emotion or "unknown"
        s = m.sentiment or "neutral"
        emotion_counts[e] = emotion_counts.get(e, 0) + 1
        sentiment_counts[s] = sentiment_counts.get(s, 0) + 1
        if m.sentiment_score: scores.append(m.sentiment_score)
        if m.crisis_flag: crisis_count += 1

    return {
        "session_id": session_id,
        "total_user_messages": len(msgs),
        "dominant_emotion_overall": max(emotion_counts, key=emotion_counts.get),
        "emotion_breakdown": emotion_counts,
        "sentiment_breakdown": sentiment_counts,
        "average_confidence": round(sum(scores)/len(scores), 2) if scores else None,
        "crisis_flag_count": crisis_count,
        "voice_message_count": sum(1 for m in msgs if m.input_type == "voice"),
        "text_message_count": sum(1 for m in msgs if m.input_type == "text"),
    }