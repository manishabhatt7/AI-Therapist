# Solace UI (Streamlit)

A self-contained, compassionate mental-health conversational interface built with **Streamlit**. It calls Solace's application services directly, so a separate FastAPI server is not required.

---

## 🌟 Features

- 🔐 **Full Authentication**: User Registration, Login (JWT stored in session state), Email Verification, and Verification Link Resend.
- 💬 **Therapeutic Chat Interface**: Conversational feed with formatted markdown responses and emotional resonance.
- 🎙️ **Voice Messaging & Audio Responses**:
  - Live microphone recording via `st.audio_input` or file upload (`.wav`, `.mp3`, `.m4a`, `.ogg`, `.webm`).
  - Automated Whisper transcription with backend analysis.
  - Spoken audio replies synthesized via Text-to-Speech (TTS).
- 📊 **Emotional Insights & Sentiment Breakdown**:
  - Primary emotion detection with confidence scoring and emoji representation.
  - Real-time sentiment breakdown (Positive, Negative, Neutral, Mixed).
  - Breakdown of detected emotions across session messages.
- 🆘 **Crisis Detection & Support Banner**:
  - Real-time crisis detection displaying helpline contacts (988 Suicide & Crisis Lifeline, Crisis Text Line).
- 🗂️ **Multi-Session Management**:
  - Create new sessions and switch between conversation histories with custom titles and dates.

---

## 🚀 Quick Start

### 1. Install Dependencies

Ensure Python 3.11+ and `uv` are installed. Inside the `frontend/` directory:

```bash
uv sync
```

### 2. Configure Environment (Optional)

Set the database, AI, email, and voice settings in `backend/.env`. Streamlit loads that shared configuration when it starts.

### 3. Run the Streamlit Application

```bash
uv run streamlit run app.py
```

The app will open automatically in your browser at:
`http://localhost:8501`

---

## 📂 Project Structure

```
frontend/
├── app.py                # Main Streamlit application entry point
├── api_client.py         # In-process bridge to Solace services
├── utils.py              # Emotion metadata, date/time formatters, audio decoding
├── styles.py             # Solace custom dark theme CSS and styling
├── pyproject.toml        # Streamlit and service dependencies
├── .streamlit/
│   └── config.toml       # Streamlit theme and server configuration
└── README.md             # This guide
```
