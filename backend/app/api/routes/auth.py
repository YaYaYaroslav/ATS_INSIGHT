from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.schemas.auth import (
    UserCreate,
    UserOut,
    Token,
    PasswordResetRequest,
    ResendVerificationRequest,
)
from app.services.email_service import generate_verification_token, send_verification_email

router = APIRouter(prefix="/auth", tags=["Authentication"])

# In-memory store for password-reset tokens. For production, back this with a
# database table and real email delivery.
_reset_tokens: dict[str, str] = {}


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="A user with this email already exists")

    token, expires = generate_verification_token()

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        is_verified=False,
        verification_token=token,
        verification_token_expires=expires,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    send_verification_email(user.email, token)

    return user


@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.verification_token == token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid verification token")

    if user.is_verified:
        # Idempotent: the link may be opened more than once (email security
        # scanners, React StrictMode in dev, a duplicate click) — not an error.
        return {"message": "Email already verified. You can log in."}

    if user.verification_token_expires and user.verification_token_expires < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="This link has expired. Request a new verification email.")

    user.is_verified = True
    db.commit()
    return {"message": "Email verified. You can now log in."}


@router.post("/resend-verification")
def resend_verification(payload: ResendVerificationRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    # Always return the same generic response to avoid leaking whether an
    # account exists or is already verified.
    if user and not user.is_verified:
        token, expires = generate_verification_token()
        user.verification_token = token
        user.verification_token_expires = expires
        db.commit()
        send_verification_email(user.email, token)

    return {"message": "If the account exists and isn't verified yet, a new email has been sent."}


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2PasswordRequestForm uses "username" — we put the email there.
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Check your inbox or request a new verification email.",
        )

    access_token = create_access_token(subject=user.email)
    return Token(access_token=access_token)


@router.post("/password-reset/request")
def request_password_reset(payload: PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    # Avoids leaking whether the email exists.
    if user:
        import secrets
        token = secrets.token_urlsafe(32)
        _reset_tokens[token] = user.email
        # TODO: send this via email_service.py instead of only storing it.
    return {"message": "If this email exists, password reset instructions have been sent."}


@router.post("/password-reset/confirm")
def confirm_password_reset(token: str, new_password: str, db: Session = Depends(get_db)):
    email = _reset_tokens.pop(token, None)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = hash_password(new_password)
    db.commit()
    return {"message": "Password updated successfully"}
