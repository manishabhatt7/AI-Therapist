# AI Therapist

## Overview

AI Therapist is a FastAPI-based backend application that provides AI-powered chat and user authentication APIs.

## Tech Stack

- Python 3.11+
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- Groq API
- Uvicorn
- uv (dependency management)

## Project Structure

```
backend/
├── app/
│   ├── auth/
│   ├── routes/
│   ├── services/
│   ├── models/
│   ├── schemas/
│   ├── database/
│   ├── config.py
│   └── main.py
├── alembic/
├── pyproject.toml
├── .env.example
└── alembic.ini
```

## Prerequisites

- Python 3.11 or newer
- PostgreSQL
- Groq API Key
- uv (recommended)

Install uv:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Setup

### 1. Navigate to backend

```bash
cd backend
```

### 2. Create environment file

```bash
cp .env.example .env
```

Update the values in `.env`, especially:

- Database connection settings
- GROQ_API_KEY
- JWT/Auth settings

### 3. Install dependencies

Using uv:

```bash
uv sync
```

### 4. Run database migrations

```bash
alembic upgrade head
```

## Running the Application

From the `backend` directory:

```bash
uv run uvicorn app.main:app --reload
```

Or:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

- http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Common Commands

### Create a migration

```bash
alembic revision --autogenerate -m "migration message"
```

### Apply migrations

```bash
alembic upgrade head
```

### Roll back one migration

```bash
alembic downgrade -1
```

## Troubleshooting

### Module not found

Ensure dependencies are installed:

```bash
uv sync
```

### Database connection errors

Verify:

- PostgreSQL is running
- `.env` values are correct
- Database exists
