import base64
from datetime import datetime
from typing import Optional, Dict, Any

# Emotion metadata matching backend sentiment service
EMOTION_META = {
    # Crisis emotions
    "desperate":   {"emoji": "🆘", "color": "#FB7185", "label": "Desperate"},
    "numb":        {"emoji": "😶", "color": "#818CF8", "label": "Numb"},
    "overwhelmed": {"emoji": "😵", "color": "#F87171", "label": "Overwhelmed"},
    "fearful":     {"emoji": "😨", "color": "#FBBF24", "label": "Fearful"},
    "ashamed":     {"emoji": "😞", "color": "#A78BFA", "label": "Ashamed"},

    # Negative emotions
    "anxious":     {"emoji": "😰", "color": "#FBBF24", "label": "Anxious"},
    "sad":         {"emoji": "😢", "color": "#60A5FA", "label": "Sad"},
    "frustrated":  {"emoji": "😤", "color": "#FB923C", "label": "Frustrated"},
    "angry":       {"emoji": "😠", "color": "#F87171", "label": "Angry"},
    "lonely":      {"emoji": "🌧️", "color": "#818CF8", "label": "Lonely"},
    "confused":    {"emoji": "😕", "color": "#A78BFA", "label": "Confused"},

    # Positive / neutral emotions
    "hopeful":     {"emoji": "🌱", "color": "#34D399", "label": "Hopeful"},
    "calm":        {"emoji": "😌", "color": "#14B8A6", "label": "Calm"},
    "grateful":    {"emoji": "🙏", "color": "#34D399", "label": "Grateful"},
    "relieved":    {"emoji": "😮‍💨", "color": "#6EE7B7", "label": "Relieved"},
    "neutral":     {"emoji": "😐", "color": "#94A3B8", "label": "Neutral"},
}

SENTIMENT_COLORS = {
    "positive": "#34D399",
    "negative": "#FB7185",
    "neutral":  "#94A3B8",
    "mixed":    "#FBBF24",
}


def get_emotion_meta(emotion: Optional[str]) -> Dict[str, str]:
    if not emotion:
        return EMOTION_META["neutral"]
    key = str(emotion).strip().lower()
    return EMOTION_META.get(key, EMOTION_META["neutral"])


def format_timestamp(iso_str: Optional[str]) -> str:
    if not iso_str:
        return ""
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%I:%M %p")
    except Exception:
        return ""


def format_session_date(iso_str: Optional[str]) -> str:
    if not iso_str:
        return "Conversation"
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
        diff = (now.date() - dt.date()).days
        if diff == 0:
            return f"Today, {dt.strftime('%I:%M %p')}"
        elif diff == 1:
            return f"Yesterday, {dt.strftime('%I:%M %p')}"
        return dt.strftime("%b %d, %Y")
    except Exception:
        return "Conversation"


def decode_base64_audio(b64_string: str) -> Optional[bytes]:
    """Decodes base64 audio string to raw bytes for st.audio."""
    try:
        return base64.b64decode(b64_string)
    except Exception:
        return None


def truncate(text: str, max_len: int = 32) -> str:
    if not text:
        return ""
    text = text.strip()
    return (text[:max_len] + "…") if len(text) > max_len else text

