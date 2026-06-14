from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.auth.auth_service import register_user, login_user, verify_email
from app.schemas.register_schemas import RegisterRequest, RegisterResponse
from app.schemas.login_schemas import LoginRequest, LoginResponse

router = APIRouter(tags=["Authentication"], prefix="/auth")


@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user and send verification email"""
    
    # Check if user already exists
    existing_user = db.query(__import__('app.database.models', fromlist=['User']).User).filter(
        __import__('app.database.models', fromlist=['User']).User.email == request.email
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    register_user(
        db,
        request.email,
        request.password,
        request.full_name
    )

    return RegisterResponse(
        message="User created. Please check your email to verify your account.",
    )


@router.get("/verify-email", include_in_schema=False)
def verify_email_endpoint(token: str, db: Session = Depends(get_db)):
    """Verify user email with token"""
    
    success = verify_email(db, token)
    
    if not success:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")
    
    return {"message": "Email verified successfully. You can now login."}


@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login user if verified"""
    
    token = login_user(
        db,
        request.email,
        request.password
    )

    if isinstance(token, dict) and "error" in token:
        raise HTTPException(status_code=token.get("status", 400), detail=token["error"])

    return LoginResponse(access_token=token)