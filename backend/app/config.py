import os 
from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __init__(self):
        self.api_version = os.getenv("version", "api/v1")
        self.app_name = os.getenv("app_name", "AI Therapist API")
        self.debug = os.getenv("debug", "false")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.model_name = os.getenv("MODEL_NAME")
        self.groq_base_url = os.getenv("GROQ_BASE_URL")
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")          # for TTS/Whisper via OpenAI
        self.whisper_backend = os.getenv("WHISPER_BACKEND", "groq")    # "groq" | "openai" | "local"
        self.enable_tts = os.getenv("ENABLE_TTS", "false").lower() == "true"
        self.DATABASE_URL = os.getenv("DATABASE_URL")
        
        # Email settings
        self.SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
        self.SMTP_USER = os.getenv("SMTP_USER")
        self.SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
        self.SENDER_EMAIL = os.getenv("SENDER_EMAIL", self.SMTP_USER)
        self.FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
        self.VERIFICATION_TOKEN_EXPIRY_MINUTES = int(os.getenv("VERIFICATION_TOKEN_EXPIRY_MINUTES", "24"))

settings = Settings()
