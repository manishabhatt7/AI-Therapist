import smtplib
from email.mime.text import MIMEText
from app.config import settings
import secrets


def generate_verification_token() -> str:
    """Create a random token for email verification"""
    return secrets.token_urlsafe(32)


def send_verification_email(email: str, verification_token: str) -> bool:
    """Send email with verification link to user"""
    try:
        verification_url = f"{settings.FRONTEND_URL}/auth/verify-email?token={verification_token}"
        
        message = MIMEText(f"Click here to verify: {verification_url}")
        message["Subject"] = f"Verify your {settings.app_name} account"
        message["From"] = settings.SENDER_EMAIL
        message["To"] = email
        
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SENDER_EMAIL, email, message.as_string())
        
        print(f"Verification email sent to {email}")
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False


def send_welcome_email(email: str) -> bool:
    """Send welcome email after verification"""
    try:
        message = MIMEText("Welcome! Your email has been verified. You can now login.")
        message["Subject"] = f"Welcome to {settings.app_name}"
        message["From"] = settings.SENDER_EMAIL
        message["To"] = email
        
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SENDER_EMAIL, email, message.as_string())
        
        print(f"Welcome email sent to {email}")
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False


