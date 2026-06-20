import json
import logging
from openai import OpenAI
from app.config import settings

logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.groq_api_key, base_url=settings.groq_base_url)

# Explicit crisis phrases used as a hard-coded safety net BEFORE the LLM runs.
# LLMs can miss obvious statements when they're short or blunt ("want to die",
# "kill myself") because they sometimes classify sentiment on surface politeness.
CRISIS_KEYWORDS = [
    "suicide", "suicidal", "kill myself", "end my life", "want to die",
    "don't want to live", "dont want to live", "no reason to live",
    "self-harm", "self harm", "cut myself", "hurt myself", "harm myself",
    "overdose", "hang myself", "jump off", "shoot myself",
    "can't go on", "cant go on", "can't take it anymore", "cant take it anymore",
    "rather be dead", "better off dead", "better off without me",
]

def _keyword_crisis_check(text: str) -> bool:
    lower = text.lower()
    return any(kw in lower for kw in CRISIS_KEYWORDS)


SENTIMENT_PROMPT = """You are a clinical emotion-analysis model embedded in a mental health support app.

Analyse the user message and return ONLY a valid JSON object — no prose, no markdown fences.

Required keys:
{
  "sentiment": "<positive | negative | neutral | mixed>",
  "sentiment_score": <float 0.0–1.0, your confidence in dominant_emotion>,
  "dominant_emotion": "<single lowercase word>",
  "secondary_emotions": ["<up to 2 additional emotions>"],
  "crisis_flag": <true | false>
}

Allowed dominant_emotion values:
anxious, sad, hopeful, frustrated, calm, angry, confused, grateful, lonely,
relieved, overwhelmed, desperate, numb, ashamed, fearful, neutral

CRITICAL crisis_flag rules — set to true for ANY of the following:
- Any mention of suicide, suicidal thoughts, or wanting to die
- Self-harm, cutting, hurting oneself
- Feeling there is no reason to live or wanting to disappear
- Expressions of hopelessness combined with phrases like "can't go on" or "give up"
- Statements that imply the person believes others would be better off without them
- Any direct or indirect indication of intent to harm themselves or others

IMPORTANT: A short blunt statement like "I want to suicide" or "I want to die" MUST
always produce crisis_flag=true and dominant_emotion="desperate" and sentiment="negative".
Do NOT let neutral phrasing mask a crisis. When in doubt, set crisis_flag=true.

Return ONLY the JSON object."""


def analyse_sentiment(text: str) -> dict:
    # 1. Hard keyword safety net — never miss obvious crisis phrases
    keyword_crisis = _keyword_crisis_check(text)

    try:
        response = client.chat.completions.create(
            model=settings.model_name,
            messages=[
                {"role": "system", "content": SENTIMENT_PROMPT},
                {"role": "user", "content": text}
            ],
            temperature=0.0,   # deterministic for safety-critical classification
            max_tokens=200
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        data = json.loads(raw)

        # 2. OR the keyword result with the LLM result — either can trigger crisis
        crisis = keyword_crisis or bool(data.get("crisis_flag", False))

        # 3. If crisis detected, override emotion to reflect severity
        dominant = data.get("dominant_emotion", "neutral")
        sentiment = data.get("sentiment", "neutral")
        if crisis and dominant in ("neutral", "calm", "confused"):
            dominant = "desperate"
            sentiment = "negative"

        return {
            "sentiment": sentiment,
            "sentiment_score": float(data.get("sentiment_score", 0.5)),
            "dominant_emotion": dominant,
            "secondary_emotions": data.get("secondary_emotions", []),
            "crisis_flag": crisis,
        }

    except Exception as e:
        logger.warning(f"Sentiment analysis failed: {e}")
        # Even on LLM failure, keyword check still applies
        return {
            "sentiment": "negative" if keyword_crisis else "neutral",
            "sentiment_score": 0.9 if keyword_crisis else 0.5,
            "dominant_emotion": "desperate" if keyword_crisis else "neutral",
            "secondary_emotions": [],
            "crisis_flag": keyword_crisis,
        }