from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.database.database import get_db
from app.database.models import User
from app.auth.auth_service import (
    register_user, login_user, verify_email, resend_verification, logout_user
)
from app.auth.auth_dependency import get_current_user
from app.schemas.register_schemas import RegisterRequest, RegisterResponse
from app.schemas.login_schemas import LoginRequest, LoginResponse

router = APIRouter(tags=["Authentication"], prefix="/auth")


class ResendRequest(BaseModel):
    email: EmailStr


# ── Register ──────────────────────────────────────────────────────

@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered.")

    register_user(db, request.email, request.password, request.full_name)
    return RegisterResponse(
        message="Account created. Please check your email to verify your account."
    )


# ── Verify email ──────────────────────────────────────────────────

@router.get("/verify-email")
def verify_email_endpoint(token: str, db: Session = Depends(get_db)):
    result = verify_email(db, token)

    if result["success"]:
        return {"message": "Email verified successfully. You can now log in."}

    if result["reason"] == "expired":
        raise HTTPException(
            status_code=400,
            detail="TOKEN_EXPIRED"  # frontend catches this specifically
        )

    raise HTTPException(status_code=400, detail="Invalid verification token.")


# ── Resend verification ───────────────────────────────────────────

@router.post("/resend-verification")
def resend_verification_endpoint(request: ResendRequest, db: Session = Depends(get_db)):
    result = resend_verification(db, request.email)

    if result["success"]:
        return {"message": "Verification email sent. Please check your inbox."}

    if result["reason"] == "already_verified":
        raise HTTPException(status_code=400, detail="This email is already verified.")

    if result["reason"] == "not_found":
        raise HTTPException(status_code=404, detail="No account found with this email.")

    raise HTTPException(status_code=500, detail="Failed to send email. Please try again.")


# ── Login ─────────────────────────────────────────────────────────

@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    result = login_user(db, request.email, request.password)

    if isinstance(result, dict) and "error" in result:
        error = result["error"]

        # Return specific error codes the frontend handles
        if error == "EMAIL_NOT_VERIFIED":
            raise HTTPException(
                status_code=403,
                detail="EMAIL_NOT_VERIFIED"
            )
        if error == "ACCOUNT_INACTIVE":
            raise HTTPException(
                status_code=403,
                detail="ACCOUNT_INACTIVE"
            )

        raise HTTPException(status_code=result.get("status", 400), detail=error)

    return LoginResponse(access_token=result)


# ── Logout ────────────────────────────────────────────────────────

@router.post("/logout")
def logout(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Server-side logout endpoint.
    Frontend MUST also delete the JWT from localStorage on receiving 200.
    """
    logout_user(db, user_id)
    return {"message": "Logged out successfully."}


