from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database.models import User
from app.auth.password_handler import hash_password, verify_password
from app.auth.jwt_handler import create_access_token
from app.modules.email_service import (
    generate_verification_token,
    send_verification_email,
    send_welcome_email,
)
from app.config import settings


def register_user(db: Session, email: str, password: str, full_name: str | None = None):
    verification_token = generate_verification_token()
    token_expiry = datetime.utcnow() + timedelta(
        minutes=settings.VERIFICATION_TOKEN_EXPIRY_MINUTES
    )
    user = User(
        email=email,
        password=hash_password(password),
        full_name=full_name,
        verification_token=verification_token,
        verification_token_expires=token_expiry,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    send_verification_email(email, verification_token)
    return user


def verify_email(db: Session, token: str) -> dict:
    """
    Returns:
      {"success": True}
      {"success": False, "reason": "expired"}   ← token exists but expired
      {"success": False, "reason": "invalid"}   ← token not found
    """
    user = db.query(User).filter(User.verification_token == token).first()

    if not user:
        return {"success": False, "reason": "invalid"}

    if user.verification_token_expires < datetime.utcnow():
        # Token expired — set is_active=False, clear token
        user.is_active = False
        user.verification_token = None
        user.verification_token_expires = None
        db.commit()
        return {"success": False, "reason": "expired"}

    user.is_verified = True
    user.is_active = True
    user.verification_token = None
    user.verification_token_expires = None
    db.commit()
    db.refresh(user)
    send_welcome_email(user.email)
    return {"success": True}


def resend_verification(db: Session, email: str) -> dict:
    """
    Regenerates the verification token and resends the email.
    Called when the user clicks "Resend verification email".
    """
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return {"success": False, "reason": "not_found"}

    if user.is_verified:
        return {"success": False, "reason": "already_verified"}

    # Generate fresh token
    new_token = generate_verification_token()
    user.verification_token = new_token
    user.verification_token_expires = datetime.utcnow() + timedelta(
        minutes=settings.VERIFICATION_TOKEN_EXPIRY_MINUTES
    )
    user.is_active = True   # reactivate so they can try again
    db.commit()

    sent = send_verification_email(email, new_token)
    if not sent:
        return {"success": False, "reason": "email_failed"}

    return {"success": True}


def login_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return {"error": "No account found with this email.", "status": 404}

    if not user.is_verified:
        return {"error": "EMAIL_NOT_VERIFIED", "status": 403}

    if not user.is_active:
        return {"error": "ACCOUNT_INACTIVE", "status": 403}

    if not verify_password(password, user.password):
        return {"error": "Invalid credentials.", "status": 401}

    token = create_access_token({"user_id": str(user.id)})
    return token


def logout_user(db: Session, user_id: str) -> bool:
    """
    Server-side logout.
    We don't blacklist JWTs (stateless), but we record the logout
    by updating is_active. The frontend deletes the token from localStorage.

    Note: existing JWT tokens remain cryptographically valid until expiry.
    For true token invalidation, a Redis-based token blacklist is needed
    (add to Phase 3 roadmap). For now this is the correct approach for
    a portfolio-grade project.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    # is_active stays True — logout is handled client-side by deleting the token
    # This endpoint exists so the frontend has a clean API call to make
    return True