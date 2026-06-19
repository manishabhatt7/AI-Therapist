import logging
from openai import OpenAI
from sqlalchemy.orm import Session

from app.config import settings
from app.prompts.therapist_prompt import THERAPIST_SYSTEM_PROMPT
from app.modules.memory_service import get_session_history, add_message_with_meta

logger = logging.getLogger(__name__)

# Groq client (used for both chat and whisper)
client = OpenAI(
    api_key=settings.groq_api_key,
    base_url=settings.groq_base_url
)


def _build_sentiment_context(sentiment_data: dict) -> str:
    """Build a hidden system note about the user's current emotional state."""
    emotion = sentiment_data.get("dominant_emotion", "neutral")
    crisis = sentiment_data.get("crisis_flag", False)

    note = f"\n\n[Therapist context – not visible to user]\nUser's current emotional state: {emotion}."
    if crisis:
        note += (
            "\n  CRISIS FLAG RAISED. The user may be in distress or at risk. "
            "Respond with warmth and empathy. Gently encourage them to contact a "
            "crisis helpline (e.g., iCall: 9152987821 in India) and a trusted person."
        )
    return note


def generate_response(
    session_id: str,
    user_message: str,
    db: Session = None,
    sentiment_data: dict = None,
    input_type: str = "text",
    transcription: str = None,
) -> str:
    """
    Generate AI therapist response using Groq LLM.

    Args:
        session_id:       Chat session UUID.
        user_message:     The message text (may be transcribed from voice).
        db:               Database session.
        sentiment_data:   Dict from sentiment_service.analyse_sentiment().
        input_type:       "text" or "voice".
        transcription:    Raw voice transcript (if different from user_message).

    Returns:
        AI-generated therapist response string.
    """
    try:
        history = get_session_history(session_id, db)

        system_content = THERAPIST_SYSTEM_PROMPT
        if sentiment_data:
            system_content += _build_sentiment_context(sentiment_data)

        messages = [{"role": "system", "content": system_content}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model=settings.model_name,
            messages=messages,
            temperature=0.75,
            max_tokens=300
        )

        ai_response = response.choices[0].message.content

        # Persist with sentiment metadata
        add_message_with_meta(
            session_id=session_id,
            role="user",
            content=user_message,
            db=db,
            input_type=input_type,
            sentiment=sentiment_data.get("sentiment") if sentiment_data else None,
            sentiment_score=sentiment_data.get("sentiment_score") if sentiment_data else None,
            dominant_emotion=sentiment_data.get("dominant_emotion") if sentiment_data else None,
            crisis_flag=sentiment_data.get("crisis_flag") if sentiment_data else None,
            transcription=transcription,
        )
        add_message_with_meta(
            session_id=session_id,
            role="assistant",
            content=ai_response,
            db=db,
        )

        return ai_response

    except Exception as e:
        logger.error(f"Groq LLM Error: {str(e)}")
        return "I'm here to listen, but something went wrong. Please try again."