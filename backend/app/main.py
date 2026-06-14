from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.chat_routes import router as chat_router
from app.auth.auth_routes import router as auth_router
from app.config import settings


app = FastAPI(
    title=settings.app_name,
    description="An API for an AI therapist that can chat with users and provide responses based on their messages.",
    version=settings.api_version
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(chat_router)



