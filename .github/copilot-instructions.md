# AI Therapist - Copilot Instructions

## Project Overview

AI Therapist is a FastAPI-based backend for a mental health support chatbot. It provides secure user authentication, email verification, and chat endpoints powered by a Groq LLM (OpenAI-compatible API). The system uses SQLAlchemy for ORM, Alembic for migrations, and supports PostgreSQL. Email notifications are sent for verification and onboarding.

## Tech Stack

- **Framework**: FastAPI
- **Language**: Python 3.11+
- **Database**: PostgreSQL (SQLAlchemy ORM)
- **Migrations**: Alembic
- **Auth**: JWT (python-jose), password hashing (passlib)
- **Email**: SMTP (email-validator, smtplib)
- **LLM**: Groq API (OpenAI-compatible)
- **Environment**: dotenv
- **Async**: asyncpg (for future async support)
- **Deployment**: Uvicorn

## Architecture & File Organization

### Directory Structure

```
backend/
  alembic.ini
  pyproject.toml
  alembic/
    env.py
    versions/
      <migration scripts>
  app/
    config.py
    main.py
    auth/
      auth_dependency.py
      auth_routes.py
      auth_service.py
      jwt_handler.py
      password_handler.py
    database/
      database.py
      models.py
    modules/
      email_service.py
      llm_service.py
      memory_service.py
    prompts/
      therapist_prompt.py
    routes/
      chat_routes.py
    safety/
    schemas/
      chat_schemas.py
      login_schemas.py
      register_schemas.py
```

### Organizational Principles

- **Feature-based grouping**: Auth, chat, and modules are separated by domain.
- **Colocation**: Related files (schemas, routes, services) are grouped.
- **Separation of concerns**: Auth, database, LLM, and email logic are modular.
- **Flat structure**: Avoid deep nesting; keep feature folders shallow.

## Import Patterns

- Use absolute imports within `backend.app.*` for all internal modules.
- Group imports: standard library, third-party, then internal.
- Example:
  ```python
  from fastapi import APIRouter
  from sqlalchemy.orm import Session

  from backend.app.auth.auth_service import register_user
  from backend.app.schemas.register_schemas import RegisterRequest
  ```

## Component Patterns

### FastAPI Routers

- Define routers in `routes/` and `auth/`.
- Use dependency injection for DB and user authentication.
- Example:
  ```python
  @router.post("/register")
  def register(request: RegisterRequest, db: Session = Depends(get_db)):
      ...
  ```

### Pydantic Schemas

- All request/response models in `schemas/`.
- Use type hints and validation.
- Example:
  ```python
  class ChatRequest(BaseModel):
      message: str
  ```

### Database Models

- All SQLAlchemy models in `database/models.py`.
- Use UUIDs for primary keys.
- Example:
  ```python
  class User(Base):
      id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
      ...
  ```

## Authentication

- JWT tokens via `python-jose`.
- Passwords hashed with `passlib`.
- Email verification required before login.
- Auth dependencies in `auth/`.

## Email

- SMTP settings in `.env` and `config.py`.
- Verification and welcome emails sent on registration/verification.

## LLM Integration

- LLM prompt in `prompts/therapist_prompt.py`.
- LLM service in `modules/llm_service.py`.
- Uses Groq API (OpenAI-compatible).

## Environment Variables

Required in `.env`:

```
DATABASE_URL=
GROQ_API_KEY=
MODEL_NAME=
GROQ_BASE_URL=
SMTP_HOST=
SMTP_PORT=
SMTP_USER=
SMTP_PASSWORD=
SENDER_EMAIL=
FRONTEND_URL=
VERIFICATION_TOKEN_EXPIRY_MINUTES=
```

## API Endpoints

- **/auth/register**: Register user, send verification email.
- **/auth/verify-email**: Verify email with token.
- **/auth/login**: Login, returns JWT if verified.
- **/chat/**: Post message, get LLM response.
- **/chat/history**: Get user chat history.

## Code Quality Standards

- Use type hints everywhere.
- Validate all input with Pydantic.
- Handle errors with FastAPI HTTPException.
- Log errors and important events.
- Keep business logic in service modules, not routes.

## Common Tasks

### Adding a New Endpoint

1. Add schema in `schemas/`.
2. Add business logic in `modules/` or `auth/`.
3. Add route in `routes/` or `auth/`.
4. Register router in `main.py`.

### Adding a New Model

1. Add model in `database/models.py`.
2. Create Alembic migration.
3. Update DB via Alembic.

### Adding a New Service

1. Add logic in `modules/`.
2. Import and use in routes as needed.

## Running & Deployment

- **Development**: `uvicorn backend.app.main:app --reload`
- **Migrations**: `alembic upgrade head`
- **Production**: Use Uvicorn/Gunicorn behind a reverse proxy.

---
