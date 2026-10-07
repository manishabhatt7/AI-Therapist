# AI Therapist (Solace)

AI Therapist is a mental-health-oriented conversational application. Its Streamlit UI directly uses the authentication, chat, email, sentiment, voice, and database services, so it runs as a single process. The FastAPI app remains available only for an optional HTTP API deployment.

## Table of Contents

- Overview
- Project layout
- Quick start
- Backend setup
- Frontend setup (Streamlit)
- Environment variables
- Running the application
- Troubleshooting
- Developer notes

## Project layout

Top-level layout:

```
README.md                # Root project documentation
backend/                 # FastAPI backend
	├── app/
	│   ├── auth/          # JWT authentication & email verification
	│   ├── routes/        # Chat & session endpoints
	│   ├── modules/       # email, llm, memory, voice, sentiment
	│   ├── database/      # SQLAlchemy models & migrations
	│   ├── prompts/       # Therapeutic prompt definitions
	│   └── main.py
	├── pyproject.toml
	└── .env.example
frontend/                # Streamlit UI
	├── app.py             # Streamlit application entry point
	├── api_client.py      # In-process bridge to application services
	├── utils.py           # Emotion metadata, audio decoding, formatters
	├── styles.py          # Custom CSS theme & styling
	├── pyproject.toml     # Streamlit and service dependencies
	├── .streamlit/        # Streamlit theme & config
	└── README.md
```

## Quick start (developer)

Prerequisites:

- Python 3.11+
- PostgreSQL (local or remote)

High-level steps:

1. Configure backend env: `cp backend/.env.example backend/.env` and update values.
2. Run migrations once (`cd backend && uv run alembic upgrade head`).
3. Launch the Streamlit UI (`cd frontend && uv run streamlit run app.py`).

## Backend setup & run

```bash
cd backend

# copy environment example
cp .env.example .env

# apply database migrations
alembic upgrade head

# run the app locally (dev)
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at:

- http://localhost:8000
- Swagger Docs: http://localhost:8000/docs

## Frontend setup & run (Streamlit)

```bash
cd frontend
uv sync
uv run streamlit run app.py
```

The Streamlit UI will be available at:

- http://localhost:8501

## Environment variables (backend)

Copy `backend/.env.example` to `backend/.env` and fill values. Important variables used by the app:

- `GROQ_API_KEY` — Groq/OpenAI API key used by the LLM integration
- `MODEL_NAME` — model name to use
- `GROQ_BASE_URL` — base URL for Groq/OpenAI-compatible API
- `OPENAI_API_KEY` — optional, used for TTS/Whisper fallback
- `WHISPER_BACKEND`, `ENABLE_TTS` — voice settings
- `POSTGRES_*` / `DATABASE_URL` — PostgreSQL connection
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SENDER_EMAIL` — SMTP for verification/welcome emails
- `VERIFICATION_TOKEN_EXPIRY_MINUTES` — token expiry (minutes)
- `FRONTEND_URL` — URL used when crafting frontend-facing links (default: `http://localhost:8501`)

## Running the application (developer)

One process is all that is needed:

```bash
cd frontend
uv run streamlit run app.py
```

The optional FastAPI app can still be started from `backend/` when an external HTTP API is specifically needed.

## Developer notes

- API routes live under `backend/app/routes`.
- Business logic and integrations are in `backend/app/modules` (LLM, email, memory, sentiment, voice).
- DB models are in `backend/app/database/models.py` and migrations are in `backend/alembic/versions`.
