"""
voice_service.py  –  Phase 2
Handles Speech-to-Text (STT) using OpenAI Whisper API.

Why Whisper?
- Best-in-class open transcription model.
- Available via OpenAI API (no GPU needed) and also runnable locally with `openai-whisper`.
- Supports 99 languages, handles accents well.

Alternative free option: use the `openai-whisper` PyPI package to run locally
(uncomment the LOCAL_WHISPER section below).

To add Text-to-Speech (TTS) for the assistant's reply, see the `synthesise_speech`
function at the bottom – it uses OpenAI TTS or gTTS as a free fallback.
"""

import io
import logging
import tempfile
import os
from typing import Optional

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────
#  Option A: Groq Whisper API (fast, free tier available)
# ─────────────────────────────────────────────────────────
def transcribe_audio_groq(audio_bytes: bytes, filename: str = "audio.webm") -> str:
    """
    Transcribes audio using Groq's Whisper endpoint.
    Groq provides Whisper large-v3 for free with generous rate limits.

    Args:
        audio_bytes: Raw audio bytes (webm, mp3, wav, ogg, m4a accepted).
        filename: Hint for the MIME type; use the original file extension.

    Returns:
        Transcribed text string.
    """
    from openai import OpenAI
    from app.config import settings

    client = OpenAI(
        api_key=settings.groq_api_key,
        base_url=settings.groq_base_url
    )

    try:
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = filename  # openai SDK uses name to infer content-type

        transcription = client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=audio_file,
            response_format="text"
        )
        return transcription.strip()

    except Exception as e:
        logger.error(f"Groq Whisper transcription error: {e}")
        raise

# ─────────────────────────────────────────────────────────
#  Option B: OpenAI Whisper API (paid but very reliable)
# ─────────────────────────────────────────────────────────
def transcribe_audio_openai(audio_bytes: bytes, filename: str = "audio.webm") -> str:
    """
    Transcribes audio using the official OpenAI Whisper API.
    Requires OPENAI_API_KEY in settings.
    """
    from openai import OpenAI
    from app.config import settings

    client = OpenAI(api_key=settings.openai_api_key)

    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = filename

    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )
    return transcription.text.strip()


# ─────────────────────────────────────────────────────────
#  Option C: Local Whisper (no API key needed, offline)
# ─────────────────────────────────────────────────────────
# Uncomment and install:  pip install openai-whisper ffmpeg-python
#
# import whisper as local_whisper
# _local_model = None
#
# def _get_local_model():
#     global _local_model
#     if _local_model is None:
#         _local_model = local_whisper.load_model("base")   # or "small", "medium"
#     return _local_model
#
# def transcribe_audio_local(audio_bytes: bytes, filename: str = "audio.webm") -> str:
#     model = _get_local_model()
#     with tempfile.NamedTemporaryFile(suffix=os.path.splitext(filename)[1], delete=False) as tmp:
#         tmp.write(audio_bytes)
#         tmp_path = tmp.name
#     try:
#         result = model.transcribe(tmp_path)
#         return result["text"].strip()
#     finally:
#         os.unlink(tmp_path)


# ─────────────────────────────────────────────────────────
#  Public interface – choose your backend here
# ─────────────────────────────────────────────────────────
def transcribe_audio(audio_bytes: bytes, filename: str = "audio.webm") -> str:
    """
    Unified transcription entry point.
    Defaults to Groq (free). Swap to `transcribe_audio_openai` or
    `transcribe_audio_local` by changing the function call below.
    """
    return transcribe_audio_groq(audio_bytes, filename)


# ─────────────────────────────────────────────────────────
#  Text-to-Speech (TTS) – optional, for voice responses
# ─────────────────────────────────────────────────────────
def synthesise_speech(text: str, voice: str = "nova") -> bytes:
    """
    Converts text to speech using OpenAI TTS.
    Returns raw MP3 bytes which the client can play.

    voice options: alloy, echo, fable, onyx, nova, shimmer
    For a free fallback, use gTTS:
        pip install gTTS
        from gtts import gTTS; import io
        tts = gTTS(text=text, lang="en"); buf = io.BytesIO(); tts.write_to_fp(buf)
        return buf.getvalue()
    """
    from openai import OpenAI
    from app.config import settings

    client = OpenAI(api_key=settings.openai_api_key)

    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text
    )
    return response.content
