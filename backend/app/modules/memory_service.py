from typing import Dict, List
from sqlalchemy.orm import Session
from app.database.models import ChatMessage

memory_store: Dict[str, List[dict]] = {}

MAX_HISTORY = 5 


def get_session_history(session_id: str, db: Session = None) -> List[dict]:
    """Get conversation history from memory or database"""
    
    # Return from in-memory if available
    if session_id in memory_store:
        return memory_store[session_id]
    
    # If database connection available, load from DB
    if db:
        messages = db.query(ChatMessage).filter(
            ChatMessage.user_id == session_id
        ).order_by(ChatMessage.created_at.desc()).limit(MAX_HISTORY).all()
        
        # Reverse to get chronological order
        history = [{
            "role": msg.role,
            "content": msg.content
        } for msg in reversed(messages)]
        
        memory_store[session_id] = history
        return history
    
    return []


def add_message(session_id: str, role: str, content: str, db: Session = None):
    """Add message to memory and optionally to database"""
    
    if session_id not in memory_store:
        memory_store[session_id] = []
    
    message_data = {
        "role": role,
        "content": content
    }
    
    memory_store[session_id].append(message_data)
    memory_store[session_id] = memory_store[session_id][-MAX_HISTORY:]
    
    # Save to database if connection available
    if db:
        chat_msg = ChatMessage(
            user_id=session_id,
            role=role,
            content=content
        )
        db.add(chat_msg)
        db.commit()


