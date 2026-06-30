"""
voice_service.py
================
STT : Groq Whisper large-v3-turbo
TTS : Groq Orpheus canopylabs/orpheus-v1-english

FALLBACK: If Orpheus is unavailable on your Groq tier, we fall back to
gTTS (Google TTS, free, no key needed). Install: pip install gTTS
"""
import io
import base64
import logging
from groq import Groq
from app.config import settings
from gtts import gTTS

logger = logging.getLogger(__name__)

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=settings.groq_api_key)
    return _client


# ── STT ──────────────────────────────────────────────────────────

def transcribe_audio(audio_bytes: bytes, filename: str = "audio.webm") -> str:
    client = _get_client()
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = filename
    try:
        transcription = client.audio.transcriptions.create(
            model="whisper-large-v3-turbo",
            file=audio_file,
            response_format="text",
        )
        return transcription.strip()
    except Exception as e:
        logger.error(f"Whisper STT error: {e}")
        raise


# ── TTS — Groq Orpheus ────────────────────────────────────────────

def _tts_orpheus(text: str, voice: str) -> bytes:
    """Primary TTS via Groq Orpheus."""
    client = _get_client()
    response = client.audio.speech.create(
        model="canopylabs/orpheus-v1-english",
        voice=voice,
        input=f"[gentle] {text}",
        response_format="wav",
    )
    return response.read()


# ── TTS — gTTS fallback (free, no key needed) ─────────────────────

def _tts_gtts_fallback(text: str) -> bytes:
    """
    Fallback TTS using Google TTS (gTTS).
    Returns MP3 bytes (not WAV, but browsers play both).
    """
    try:
        buf = io.BytesIO()
        gTTS(text=text, lang="en", slow=False).write_to_fp(buf)
        buf.seek(0)
        return buf.read()
    except ImportError:
        logger.error(
            "gTTS not installed. Run: pip install gTTS\n"
            "Or check your Groq API key has TTS access at https://console.groq.com"
        )
        raise
    except Exception as e:
        logger.error(f"gTTS fallback error: {e}")
        raise


def synthesise_speech(text: str, voice: str = "hannah") -> tuple[bytes, str]:
    """
    Returns (audio_bytes, mime_type).
    Tries Orpheus first, falls back to gTTS.
    mime_type is 'audio/wav' or 'audio/mpeg' — frontend needs this.
    """
    # Try Groq Orpheus
    try:
        wav_bytes = _tts_orpheus(text, voice)
        logger.info(f"TTS (Orpheus): {len(wav_bytes)} bytes")
        return wav_bytes, "audio/wav"
    except Exception as e:
        logger.warning(f"Orpheus TTS failed ({e}), trying gTTS fallback...")

    # Fallback to gTTS
    try:
        mp3_bytes = _tts_gtts_fallback(text)
        logger.info(f"TTS (gTTS fallback): {len(mp3_bytes)} bytes")
        return mp3_bytes, "audio/mpeg"
    except Exception as e:
        logger.error(f"All TTS options failed: {e}")
        raise


def synthesise_speech_base64(text: str, voice: str = "hannah") -> tuple[str, str]:
    """
    Returns (base64_string, mime_type).
    Frontend uses mime_type to build the correct data URL:
      data:{mime_type};base64,{base64_string}
    """
    audio_bytes, mime_type = synthesise_speech(text, voice)
    b64 = base64.b64encode(audio_bytes).decode("utf-8")
    return b64, mime_type