import os 
from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __init__(self):
        self.api_version = os.getenv("version", "api/v1")
        self.app_name = os.getenv("app_name", "AI Therapist API")
        self.debug = os.getenv("debug", "false")
        # Groq Settings
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        
        self.llm_model = os.getenv("LLM_MODEL", os.getenv("MODEL_NAME", "openai/gpt-oss-20b"))
        self.model_name = self.llm_model
        self.sentiment_model = os.getenv("SENTIMENT_MODEL", "llama-3.1-8b-instant")
        self.whisper_model = os.getenv("WHISPER_MODEL", "whisper-large-v3-turbo")
        self.tts_model = os.getenv("TTS_MODEL", "canopylabs/orpheus-v1-english")
        self.tts_voice = os.getenv("TTS_VOICE", "hannah")
        
        # Clean up GROQ_BASE_URL if it includes /openai/v1 to prevent duplicate paths (/openai/v1/openai/v1)
        raw_groq_base = os.getenv("GROQ_BASE_URL", "").strip()
        if raw_groq_base.endswith("/openai/v1"):
            raw_groq_base = raw_groq_base[:-len("/openai/v1")].rstrip("/")
            if raw_groq_base:
                os.environ["GROQ_BASE_URL"] = raw_groq_base
            else:
                os.environ.pop("GROQ_BASE_URL", None)
        self.groq_base_url = raw_groq_base or None
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
        self.FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8501")
        self.VERIFICATION_TOKEN_EXPIRY_MINUTES = int(os.getenv("VERIFICATION_TOKEN_EXPIRY_MINUTES", "24"))

settings = Settings()
