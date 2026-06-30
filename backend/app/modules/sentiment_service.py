"""
sentiment_service.py
====================
Uses qwen/qwen3-32b with reasoning_effort="none" to prevent <think> leakage
into JSON output, and with response_format=json_object for clean parsing.
"""
import re
import json
import logging
from groq import Groq
from app.config import settings

logger = logging.getLogger(__name__)

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=settings.groq_api_key)
    return _client


# ── Layer 1: keyword safety net ──────────────────────────────────
CRISIS_KEYWORDS = [
    "suicide", "suicidal", "kill myself", "killing myself",
    "end my life", "want to die", "going to die",
    "don't want to live", "dont want to live", "no reason to live",
    "self-harm", "self harm", "cut myself", "hurt myself", "harm myself",
    "will harm myself", "going to harm", "overdose", "hang myself",
    "jump off", "shoot myself", "can't go on", "cant go on",
    "can't take it anymore", "cant take it anymore",
    "rather be dead", "better off dead", "better off without me",
    "end it all", "don't want to be here", "dont want to be here",
    "life is not worth", "not worth living", "take my own life",
    "disappear forever", "everyone would be better",
    "will suicide", "i will suicide",
]

def _keyword_crisis_check(text: str) -> bool:
    lower = text.lower()
    return any(kw in lower for kw in CRISIS_KEYWORDS)


def _strip_think(text: str) -> str:
    """Strip Qwen3 <think> blocks if they leak into JSON output."""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


# ── Layer 2: LLM classification ───────────────────────────────────
SENTIMENT_SYSTEM_PROMPT = """\
You are a clinical emotion classifier for a mental health application.
Your output directly affects patient safety. Return ONLY valid JSON.

Schema:
{
  "sentiment": "positive" | "negative" | "neutral" | "mixed",
  "sentiment_score": <float 0.0-1.0>,
  "dominant_emotion": <see allowed values>,
  "secondary_emotions": [<up to 2>],
  "crisis_flag": true | false,
  "crisis_reasoning": "<one sentence or 'none'>"
}

Allowed dominant_emotion:
anxious, sad, hopeful, frustrated, calm, angry, confused, grateful,
lonely, relieved, overwhelmed, desperate, numb, ashamed, fearful, neutral

CRISIS FLAG — set true for ANY of:
- Mentions of suicide, wanting to die, killing oneself
- Self-harm, cutting, hurting oneself
- "I will harm myself", "I will suicide", "killing myself"
- Feeling life has no point or others would be better off without them
- Hopelessness combined with helplessness

IMPORTANT: "I will suicide" and "I am killing myself" MUST produce crisis_flag=true.
When crisis_flag=true, dominant_emotion must be: desperate, numb, overwhelmed, or fearful.
Return ONLY the JSON object. No explanation. No markdown."""


def analyse_sentiment(text: str) -> dict:
    keyword_crisis = _keyword_crisis_check(text)

    try:
        client = _get_client()

        response = client.chat.completions.create(
            model="qwen/qwen3-32b",
            messages=[
                {"role": "system", "content": SENTIMENT_SYSTEM_PROMPT},
                {"role": "user",   "content": text},
            ],
            temperature=0.0,
            max_tokens=200,
            reasoning_effort="none",                        # disable <think> blocks
            response_format={"type": "json_object"},        # force valid JSON output
        )

        raw  = _strip_think(response.choices[0].message.content.strip())
        data = json.loads(raw)

        llm_crisis = bool(data.get("crisis_flag", False))
        crisis     = keyword_crisis or llm_crisis

        dominant  = data.get("dominant_emotion", "neutral")
        sentiment = data.get("sentiment", "neutral")

        if crisis and dominant in ("neutral", "calm", "confused", "hopeful", "grateful"):
            dominant  = "desperate"
            sentiment = "negative"

        return {
            "sentiment":         sentiment,
            "sentiment_score":   float(data.get("sentiment_score", 0.5)),
            "dominant_emotion":  dominant,
            "secondary_emotions": data.get("secondary_emotions", []),
            "crisis_flag":       crisis,
            "crisis_reasoning":  data.get("crisis_reasoning", "none"),
        }

    except Exception as e:
        logger.warning(f"Sentiment analysis failed: {e}")
        return {
            "sentiment":         "negative" if keyword_crisis else "neutral",
            "sentiment_score":   0.95 if keyword_crisis else 0.5,
            "dominant_emotion":  "desperate" if keyword_crisis else "neutral",
            "secondary_emotions": [],
            "crisis_flag":       keyword_crisis,
            "crisis_reasoning":  "keyword match" if keyword_crisis else "none",
        }