# AI Therapist

AI Therapist is an experimental mental-health-oriented chat application with a FastAPI backend and a React frontend. The backend provides authenticated chat endpoints, email verification, and integration with an LLM (Groq/OpenAI). The frontend is a small React app that talks to the API.

## Table of Contents

- Overview
- Project layout
- Quick start
- Backend setup
- Frontend setup
- Environment variables
- Running both services
- Troubleshooting
- Developer notes

## Project layout

Top-level layout (simplified):

```
README.md                # <-- this file (root)
backend/                 # FastAPI backend
	├── app/
	│   ├── auth/
	│   ├── routes/
	│   ├── modules/       # email, llm, memory, voice, sentiment
	│   ├── database/
	│   ├── prompts/
	│   └── main.py
	├── pyproject.toml
	└── .env.example
frontend/                # React frontend (Create React App)
	├── package.json
	└── src/
```

## Quick start (developer)

Prerequisites:

- Python 3.11+
- Node.js (LTS recommended, 18+ tested)
- PostgreSQL (local or remote)
- (optional) `uv` dependency manager — used in this repo but not required

High-level steps:

1. Configure backend env: `cp backend/.env.example backend/.env` and update values.
2. Install backend dependencies and run migrations.
3. Start the backend server.
4. Install frontend dependencies and start the frontend.

See the sections below for commands and troubleshooting notes.

## Backend setup & run

Recommended (using `uv`) — simple and matches the repo docs:

```bash
cd backend

# create/activate a virtualenv (recommended) and sync dependencies
# install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync

# copy environment example
cp .env.example .env

# apply migrations
alembic upgrade head

# run the app locally (dev)
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
# or
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

If you don't use `uv`: after creating and activating the venv, install packages manually (or via your preferred tool) and run the `uvicorn` command shown above.

The API will be available at:

- http://localhost:8000
- Swagger: http://localhost:8000/docs

## Frontend setup & run

The frontend is a Create-React-App project in `frontend/`.

```bash
cd frontend
npm install
npm start
```

If you see `sh: 1: react-scripts: not found` when running `npm start`:

1. Ensure `npm install` completed without errors.
2. Try installing `react-scripts` explicitly:

```bash
npm install --save-dev react-scripts@5.0.1
# then
npm start
```

3. Check `node -v` and use a supported Node version (LTS 18+ recommended).

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
- `FRONTEND_URL` — URL used when crafting frontend-facing links (default: `http://localhost:3000`)
- `BACKEND_URL` — URL used when crafting backend verification links (default: `http://localhost:8000`)

See `backend/.env.example` for the complete example.

## Troubleshooting (common issues)

- ERR_CONNECTION_REFUSED (email verification): Backend not running or wrong `BACKEND_URL`. Start backend and/or update `BACKEND_URL` in `backend/.env`.

- `react-scripts: not found`: Run `npm install` in `frontend/`, then `npm start`. If still failing, install `react-scripts` explicitly as shown above.

- `TypeError: generate_response() got an unexpected keyword argument 'sentiment_data'`: This commonly indicates the running process is using an older/stale version of the code. Restart the backend server (stop and run `uvicorn ... --reload` again). To inspect what the running module exposes, run:

```bash
python -c "import inspect; from app.modules import llm_service; print(inspect.signature(llm_service.generate_response)); print(llm_service.generate_response.__module__)"
```

- Database connection problems: verify `DATABASE_URL`, ensure Postgres is running and reachable from the backend host.

- SMTP/email errors: verify SMTP credentials and that the SMTP provider allows SMTP connections from your environment (Gmail requires App Passwords or OAuth).

## Running backend + frontend together (developer)

Open two terminals:

Terminal 1 — backend:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Terminal 2 — frontend:

```bash
cd frontend
npm start
```

The frontend is configured to proxy API requests to `http://localhost:8000` (see `frontend/package.json`).

## Developer notes

- API routes live under `backend/app/routes`.
- Business logic and integrations are in `backend/app/modules` (LLM, email, memory, sentiment, voice).
- DB models are in `backend/app/database/models.py` and migrations are in `backend/alembic/versions`.
