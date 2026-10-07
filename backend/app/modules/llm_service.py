"""
llm_service.py
==============
Generates therapeutic responses using the LLM model configured in .env / settings.
Persists conversation history with emotional context in the database.
"""
import re
import logging
from groq import Groq
from sqlalchemy.orm import Session

from app.config import settings
from app.prompts.therapist_prompt import THERAPIST_SYSTEM_PROMPT
from app.modules.memory_service import get_session_history, add_message_with_meta

logger = logging.getLogger(__name__)

_client = None


def _get_client():
    global _client
    if _client is None:
        kwargs = {"api_key": settings.groq_api_key}
        if settings.groq_base_url:
            kwargs["base_url"] = settings.groq_base_url
        _client = Groq(**kwargs)
    return _client


def _strip_think(text: str) -> str:
    """Strip <think>...</think> reasoning blocks from response if present."""
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return cleaned.strip()


def _build_sentiment_context(sentiment_data: dict) -> str:
    emotion   = sentiment_data.get("dominant_emotion", "neutral")
    crisis    = sentiment_data.get("crisis_flag", False)
    reasoning = sentiment_data.get("crisis_reasoning", "")

    note = f"\n\n[THERAPIST CONTEXT — hidden from user]\nDetected emotion: {emotion}."
    if crisis:
        note += (
            f"\n CRISIS FLAG ACTIVE. Reason: {reasoning}. "
            "Respond with deep empathy. Prioritise safety. "
            "Warmly encourage the user to contact a crisis helpline. "
            "iCall (India): 9152987821 | Vandrevala Foundation: 1860-2662-345 (24/7)"
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
    # 1. ALWAYS persist the user message to database
    try:
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
    except Exception as e:
        logger.error(f"Error persisting user message to DB: {e}")

    ai_response = ""
    try:
        history = get_session_history(session_id, db)
        client = _get_client()
        system_content = THERAPIST_SYSTEM_PROMPT

        if sentiment_data:
            system_content += _build_sentiment_context(sentiment_data)

        messages = [{"role": "system", "content": system_content}]

        # Append previous conversation history
        for msg in history:
            if isinstance(msg, dict) and msg.get("role") in ("user", "assistant") and msg.get("content"):
                messages.append({"role": msg["role"], "content": msg["content"]})

        # Avoid duplicating current user message if already present at the end
        if not history or history[-1].get("content") != user_message:
            messages.append({"role": "user", "content": user_message})

        model_name = settings.llm_model

        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.75,
            max_tokens=400,
        )
        raw = response.choices[0].message.content
        ai_response = _strip_think(raw)

    except Exception as e:
        logger.error(f"LLM generation error with model '{settings.llm_model}': {e}", exc_info=True)
        ai_response = "I hear you, and I am here for you. Could you share a little more about how that is making you feel?"

    # 2. ALWAYS persist the assistant response to database
    try:
        add_message_with_meta(
            session_id=session_id,
            role="assistant",
            content=ai_response,
            db=db,
        )
    except Exception as e:
        logger.error(f"Error persisting assistant message to DB: {e}")

    return ai_response