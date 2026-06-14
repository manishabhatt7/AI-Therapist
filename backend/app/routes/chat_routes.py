from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.auth_dependency import get_current_user
from app.database.database import get_db
from app.database.models import ChatMessage, ChatSession
from app.modules.llm_service import generate_response
from app.schemas.chat_schemas import ChatRequest, ChatResponse, ChatSessionCreate, ChatSessionOut, ChatMessageOut

router = APIRouter(tags=["Chat"], prefix="/chat")


# Create a new chat session
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

# List all chat sessions for the user
@router.get("/sessions", response_model=list[ChatSessionOut])
def list_sessions(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sessions = db.query(ChatSession).filter(ChatSession.user_id == user_id).order_by(ChatSession.created_at.desc()).all()
    return sessions

# Send a message to a session
@router.post("/sessions/{session_id}/message", response_model=ChatResponse)
def chat_in_session(
    session_id: str,
    request: ChatRequest,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validate session ownership
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == user_id).first()
    if not session:
        return {"error": "Session not found"}

    response = generate_response(
        session_id=session_id,
        user_message=request.message,
        db=db
    )

    return ChatResponse(response=response)

# Get messages for a session
@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageOut])
def get_session_messages(
    session_id: str,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50
):
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == user_id).first()
    if not session:
        return []
    messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.asc()).limit(limit).all()
    return [
        ChatMessageOut(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            created_at=msg.created_at
        ) for msg in messages
    ]



# (Optional) Keep old history endpoint for compatibility
@router.get("/history")
def get_chat_history(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50
):
    messages = db.query(ChatMessage).filter(
        ChatMessage.user_id == user_id
    ).order_by(ChatMessage.created_at.asc()).limit(limit).all()
    return {
        "messages": [
            {
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at
            }
            for msg in messages
        ]
    }
