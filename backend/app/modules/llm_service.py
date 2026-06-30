"""
llm_service.py
==============
Qwen3 models output <think>...</think> blocks before the actual response
when reasoning mode is active. We must strip these before returning to the user
and before saving to DB or sending to TTS.

Two fixes applied:
  1. reasoning_effort="none"  — disables thinking mode entirely (fastest, cleanest)
  2. _strip_think()           — fallback strip in case the tag still appears
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
        _client = Groq(api_key=settings.groq_api_key)
    return _client


def _strip_think(text: str) -> str:
    """
    Remove Qwen3 <think>...</think> reasoning blocks from the response.
    These appear when reasoning_effort is not set to 'none'.
    We strip them as a safety net even when reasoning is disabled.
    """
    # Remove <think>...</think> including everything inside (non-greedy, dotall)
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return cleaned.strip()


def _build_sentiment_context(sentiment_data: dict) -> str:
    emotion    = sentiment_data.get("dominant_emotion", "neutral")
    crisis     = sentiment_data.get("crisis_flag", False)
    reasoning  = sentiment_data.get("crisis_reasoning", "")

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
    try:
        history        = get_session_history(session_id, db)
        client         = _get_client()
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
            max_tokens=400,
            # KEY FIX: disable Qwen3 thinking/reasoning mode entirely.
            # Without this, the model prepends <think>...</think> to every response.
            # "none" = non-thinking mode — faster, no reasoning leak.
            reasoning_effort="none",
        )

        raw         = response.choices[0].message.content
        ai_response = _strip_think(raw)   # belt-and-suspenders strip

        add_message_with_meta(
            session_id=session_id, role="user", content=user_message, db=db,
            input_type=input_type,
            sentiment=sentiment_data.get("sentiment")        if sentiment_data else None,
            sentiment_score=sentiment_data.get("sentiment_score") if sentiment_data else None,
            dominant_emotion=sentiment_data.get("dominant_emotion") if sentiment_data else None,
            crisis_flag=sentiment_data.get("crisis_flag")    if sentiment_data else None,
            transcription=transcription,
        )
        add_message_with_meta(
            session_id=session_id, role="assistant", content=ai_response, db=db,
        )

        return ai_response

    except Exception as e:
        logger.error(f"LLM error: {e}")
        return "I'm here to listen, but something went wrong on my end. Please try again."