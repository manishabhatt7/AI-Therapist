from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database.models import User
from app.auth.password_handler import hash_password, verify_password
from app.auth.jwt_handler import create_access_token
from app.modules.email_service import generate_verification_token, send_verification_email, send_welcome_email
from app.config import settings


def register_user(db: Session, email: str, password: str, full_name: str | None = None):
    """Register a new user and send verification email"""
    
    # Generate verification token
    verification_token = generate_verification_token()
    token_expiry = datetime.utcnow() + timedelta(
        minutes=settings.VERIFICATION_TOKEN_EXPIRY_MINUTES
    )
    
    user = User(
        email=email,
        password=hash_password(password),
        full_name=full_name,
        verification_token=verification_token,
        verification_token_expires=token_expiry
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Send verification email
    email_result = send_verification_email(email, verification_token)
    if not email_result:
        print(f"Failed to send verification email to {email}")
    return user


def verify_email(db: Session, token: str) -> bool:
    """Verify user email with token"""
    
    user = db.query(User).filter(
        User.verification_token == token
    ).first()
    
    if not user:
        return False
    
    # Check if token has expired
    if user.verification_token_expires < datetime.utcnow():
        return False
    
    # Mark user as verified
    user.is_verified = True
    user.verification_token = None
    user.verification_token_expires = None
    
    db.commit()
    db.refresh(user)
    
    # Send welcome email
    send_welcome_email(user.email)
    
    return True


def login_user(db: Session, email: str, password: str):
    """Login user if verified and password is correct"""
    
    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user:
        return {"error": "No account found with this email. Please register first.", "status": 404}
    
    # Check if user is verified
    if not user.is_verified:
        return {"error": "Please verify your email first", "status": 403}
    
    if not verify_password(password, user.password):
        return {"error": "Invalid credentials", "status": 401}

    token = create_access_token(
        {"user_id": str(user.id)}
    )

    return token