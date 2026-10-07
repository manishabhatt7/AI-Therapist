"""In-process application service used by the Streamlit UI.

It calls the existing application logic directly instead of making HTTP
requests to a separately running FastAPI server.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable, List, Optional, Tuple, TypeVar

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_ROOT = PROJECT_ROOT / "backend"
load_dotenv(BACKEND_ROOT / ".env")
# `app.py` is also the Streamlit entry-point name.  Put backend/ first even if
# it is already somewhere on sys.path, otherwise `import app...` can resolve
# to frontend/app.py and create a circular import.
sys.path = [path for path in sys.path if path != str(BACKEND_ROOT)]
sys.path.insert(0, str(BACKEND_ROOT))

from app.auth.auth_service import (  # noqa: E402
    login_user, logout_user, register_user, resend_verification, verify_email,
)
from app.auth.jwt_handler import decode_token  # noqa: E402
from app.database.database import SessionLocal  # noqa: E402
from app.database.models import ChatMessage, ChatSession, User  # noqa: E402
from app.modules.llm_service import generate_response  # noqa: E402
from app.modules.sentiment_service import analyse_sentiment  # noqa: E402
from app.modules.voice_service import synthesise_speech_base64, transcribe_audio  # noqa: E402
from jose import JWTError  # noqa: E402

Result = Tuple[bool, Any]
T = TypeVar("T")


def upgrade_database_to_head() -> None:
    """Apply all pending Alembic revisions using the shared backend settings."""
    from alembic import command
    from alembic.config import Config

    config = Config(str(BACKEND_ROOT / "alembic.ini"))
    # Keep migration discovery independent of the directory used to launch
    # Streamlit (for example, `frontend/` locally or a hosting workdir).
    config.set_main_option("script_location", str(BACKEND_ROOT / "alembic"))
    try:
        command.upgrade(config, "head")
    except Exception as error:
        raise RuntimeError(f"Database migration failed: {error}") from error


class APIClient:
    """Compatibility facade for the UI, backed by local Python calls."""

    @staticmethod
    def _run(operation: Callable[[Any], T]) -> Result:
        db = SessionLocal()
        try:
            return True, operation(db)
        except ValueError as error:
            db.rollback()
            return False, str(error)
        except Exception as error:
            db.rollback()
            return False, f"Unexpected error: {error}"
        finally:
            db.close()

    @staticmethod
    def _user_id(token: str, db: Any) -> str:
        try:
            user_id = decode_token(token).get("user_id")
        except JWTError as error:
            raise ValueError("Your session has expired. Please sign in again.") from error
        if not user_id or not db.query(User.id).filter(User.id == user_id).first():
            raise ValueError("Your session is no longer valid. Please sign in again.")
        return str(user_id)

    @staticmethod
    def _message_dict(message: ChatMessage) -> dict[str, Any]:
        return {
            "id": message.id, "role": message.role, "content": message.content,
            "input_type": message.input_type, "sentiment": message.sentiment,
            "dominant_emotion": message.dominant_emotion,
            "transcription": message.transcription, "crisis_flag": message.crisis_flag,
            "created_at": message.created_at.isoformat() if message.created_at else None,
        }

    def register(self, email: str, password: str, full_name: str) -> Result:
        def operation(db: Any) -> dict[str, str]:
            if db.query(User).filter(User.email == email).first():
                raise ValueError("Email already registered.")
            register_user(db, email, password, full_name)
            return {"message": "Account created. Please check your email to verify your account."}
        return self._run(operation)

    def login(self, email: str, password: str) -> Result:
        def operation(db: Any) -> dict[str, str]:
            result = login_user(db, email, password)
            if isinstance(result, dict):
                raise ValueError(result["error"])
            return {"access_token": result, "token_type": "bearer"}
        return self._run(operation)

    def verify_email(self, token: str) -> Result:
        def operation(db: Any) -> dict[str, str]:
            result = verify_email(db, token)
            if result["success"]:
                return {"message": "Email verified successfully. You can now sign in."}
            raise ValueError("TOKEN_EXPIRED" if result["reason"] == "expired" else "Invalid verification token.")
        return self._run(operation)

    def resend_verification(self, email: str) -> Result:
        def operation(db: Any) -> dict[str, str]:
            result = resend_verification(db, email)
            if result["success"]:
                return {"message": "Verification email sent. Please check your inbox."}
            errors = {"already_verified": "This email is already verified.", "not_found": "No account found with this email.", "email_failed": "Failed to send email. Please try again."}
            raise ValueError(errors.get(result["reason"], "Failed to send email. Please try again."))
        return self._run(operation)

    def logout(self, token: str) -> Result:
        def operation(db: Any) -> dict[str, str]:
            logout_user(db, self._user_id(token, db))
            return {"message": "Logged out successfully."}
        return self._run(operation)

    def list_sessions(self, token: str) -> Result:
        def operation(db: Any) -> List[dict[str, Any]]:
            user_id = self._user_id(token, db)
            sessions = db.query(ChatSession).filter(ChatSession.user_id == user_id).order_by(ChatSession.created_at.desc()).all()
            return [{"id": item.id, "user_id": item.user_id, "created_at": item.created_at.isoformat()} for item in sessions]
        return self._run(operation)

    def create_session(self, token: str) -> Result:
        def operation(db: Any) -> dict[str, Any]:
            session = ChatSession(user_id=self._user_id(token, db))
            db.add(session); db.commit(); db.refresh(session)
            return {"id": session.id, "user_id": session.user_id, "created_at": session.created_at.isoformat()}
        return self._run(operation)

    def get_messages(self, token: str, session_id: str, limit: int = 50) -> Result:
        def operation(db: Any) -> List[dict[str, Any]]:
            user_id = self._user_id(token, db)
            session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == user_id).first()
            if not session:
                raise ValueError("Session not found.")
            messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.asc()).limit(limit).all()
            return [self._message_dict(message) for message in messages]
        return self._run(operation)

    def _reply(self, db: Any, user_id: str, session_id: str, message: str, input_type: str, transcription: Optional[str], tts: bool) -> dict[str, Any]:
        session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == user_id).first()
        if not session:
            raise ValueError("Session not found.")
        sentiment = analyse_sentiment(message)
        response = generate_response(session_id=session_id, user_message=message, db=db, sentiment_data=sentiment, input_type=input_type, transcription=transcription)
        audio_base64, audio_mime = None, None
        if tts:
            try:
                audio_base64, audio_mime = synthesise_speech_base64(response)
            except Exception:
                pass  # A text response remains useful when TTS is unavailable.
        return {"response": response, "sentiment": sentiment.get("sentiment"), "dominant_emotion": sentiment.get("dominant_emotion"), "crisis_flag": sentiment.get("crisis_flag"), "audio_base64": audio_base64, "audio_mime": audio_mime}

    def send_message(self, token: str, session_id: str, message: str, tts: bool = True) -> Result:
        return self._run(lambda db: self._reply(db, self._user_id(token, db), session_id, message, "text", None, tts))

    def send_voice_message(self, token: str, session_id: str, audio_bytes: bytes, filename: str = "recording.wav", tts: bool = True) -> Result:
        def operation(db: Any) -> dict[str, Any]:
            if not audio_bytes:
                raise ValueError("Empty audio file.")
            try:
                transcription = transcribe_audio(audio_bytes, filename=filename)
            except Exception as error:
                raise ValueError(f"Transcription failed: {error}") from error
            if not transcription.strip():
                raise ValueError("Could not transcribe audio.")
            return {"transcription": transcription, **self._reply(db, self._user_id(token, db), session_id, transcription, "voice", transcription, tts)}
        return self._run(operation)

    def get_sentiment_summary(self, token: str, session_id: str) -> Result:
        def operation(db: Any) -> dict[str, Any]:
            user_id = self._user_id(token, db)
            session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == user_id).first()
            if not session:
                raise ValueError("Session not found.")
            messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id, ChatMessage.role == "user", ChatMessage.sentiment.isnot(None)).all()
            if not messages:
                return {"message": "No sentiment data yet."}
            emotions: dict[str, int] = {}
            sentiments: dict[str, int] = {}
            scores: list[float] = []
            for message in messages:
                emotion, sentiment = message.dominant_emotion or "unknown", message.sentiment or "neutral"
                emotions[emotion] = emotions.get(emotion, 0) + 1
                sentiments[sentiment] = sentiments.get(sentiment, 0) + 1
                if message.sentiment_score is not None:
                    scores.append(message.sentiment_score)
            return {"session_id": session_id, "total_user_messages": len(messages), "dominant_emotion_overall": max(emotions, key=emotions.get), "emotion_breakdown": emotions, "sentiment_breakdown": sentiments, "average_confidence": round(sum(scores) / len(scores), 2) if scores else None, "crisis_flag_count": sum(bool(message.crisis_flag) for message in messages), "voice_message_count": sum(message.input_type == "voice" for message in messages), "text_message_count": sum(message.input_type == "text" for message in messages)}
        return self._run(operation)
