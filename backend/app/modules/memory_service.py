"""
memory_service.py
Manages in-memory conversation history + DB persistence.
Phase 2 adds sentiment metadata columns to ChatMessage.
"""
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from app.database.models import ChatMessage

memory_store: Dict[str, List[dict]] = {}
MAX_HISTORY = 10   # increased from 5 for better context


def get_session_history(session_id: str, db: Session = None) -> List[dict]:
    """Return the last MAX_HISTORY messages as OpenAI-compatible dicts."""
    if session_id in memory_store:
        return memory_store[session_id]

    if db:
        messages = (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(MAX_HISTORY)
            .all()
        )
        history = [{"role": msg.role, "content": msg.content} for msg in reversed(messages)]
        memory_store[session_id] = history
        return history

    return []


def add_message_with_meta(
    session_id: str,
    role: str,
    content: str,
    db: Session = None,
    input_type: str = "text",
    sentiment: Optional[str] = None,
    sentiment_score: Optional[float] = None,
    dominant_emotion: Optional[str] = None,
    crisis_flag: Optional[bool] = None,
    transcription: Optional[str] = None,
):
    """Persist a message with optional sentiment metadata."""
    if session_id not in memory_store:
        memory_store[session_id] = []

    memory_store[session_id].append({"role": role, "content": content})
    memory_store[session_id] = memory_store[session_id][-MAX_HISTORY:]

    if db:
        # We need user_id; fetch from session
        from app.database.models import ChatSession
        session_obj = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        user_id = session_obj.user_id if session_obj else session_id

        chat_msg = ChatMessage(
            user_id=user_id,
            session_id=session_id,
            role=role,
            content=content,
            input_type=input_type,
            sentiment=sentiment,
            sentiment_score=sentiment_score,
            dominant_emotion=dominant_emotion,
            crisis_flag=crisis_flag,
            transcription=transcription,
        )
        db.add(chat_msg)
        db.commit()


# Backward-compat alias used in old routes
def add_message(session_id: str, role: str, content: str, db: Session = None):
    add_message_with_meta(session_id, role, content, db)