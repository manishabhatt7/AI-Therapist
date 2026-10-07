"""
voice_service.py
================
STT : Whisper via Groq (configured via settings.whisper_model)
TTS : Orpheus via Groq (configured via settings.tts_model) with gTTS fallback
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
        kwargs = {"api_key": settings.groq_api_key}
        if settings.groq_base_url:
            kwargs["base_url"] = settings.groq_base_url
        _client = Groq(**kwargs)
    return _client


# ── STT ──────────────────────────────────────────────────────────

def transcribe_audio(audio_bytes: bytes, filename: str = "audio.webm") -> str:
    client = _get_client()
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = filename
    try:
        transcription = client.audio.transcriptions.create(
            model=settings.whisper_model,
            file=audio_file,
            response_format="text",
        )
        return transcription.strip()
    except Exception as e:
        logger.error(f"Whisper STT error using model '{settings.whisper_model}': {e}", exc_info=True)
        raise


# ── TTS — Groq Orpheus ────────────────────────────────────────────

def _tts_orpheus(text: str, voice: str) -> bytes:
    """Primary TTS via Groq Orpheus."""
    client = _get_client()
    response = client.audio.speech.create(
        model=settings.tts_model,
        voice=voice,
        input=f"[gentle] {text}",
        response_format="wav",
    )
    return response.read()


# ── TTS — gTTS fallback (free, no key needed) ─────────────────────

def _tts_gtts_fallback(text: str) -> bytes:
    """
    Fallback TTS using Google TTS (gTTS).
    Returns MP3 bytes.
    """
    try:
        buf = io.BytesIO()
        gTTS(text=text, lang="en", slow=False).write_to_fp(buf)
        buf.seek(0)
        return buf.read()
    except ImportError:
        logger.error("gTTS not installed. Run: pip install gTTS")
        raise
    except Exception as e:
        logger.error(f"gTTS fallback error: {e}")
        raise


def synthesise_speech(text: str, voice: str = None) -> tuple[bytes, str]:
    """
    Returns (audio_bytes, mime_type).
    Tries primary TTS model first, falls back to gTTS.
    """
    voice_to_use = voice or settings.tts_voice or "hannah"

    # Try Groq Orpheus
    try:
        wav_bytes = _tts_orpheus(text, voice_to_use)
        logger.info(f"TTS ({settings.tts_model}): {len(wav_bytes)} bytes")
        return wav_bytes, "audio/wav"
    except Exception as e:
        logger.warning(f"Orpheus TTS model '{settings.tts_model}' failed ({e}), trying gTTS fallback...")

    # Fallback to gTTS
    try:
        mp3_bytes = _tts_gtts_fallback(text)
        logger.info(f"TTS (gTTS fallback): {len(mp3_bytes)} bytes")
        return mp3_bytes, "audio/mpeg"
    except Exception as e:
        logger.error(f"All TTS options failed: {e}")
        raise


def synthesise_speech_base64(text: str, voice: str = None) -> tuple[str, str]:
    """
    Returns (base64_string, mime_type).
    """
    audio_bytes, mime_type = synthesise_speech(text, voice)
    b64 = base64.b64encode(audio_bytes).decode("utf-8")
    return b64, mime_type