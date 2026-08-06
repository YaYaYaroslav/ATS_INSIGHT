from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.schemas.auth import UserCreate, UserOut, Token, PasswordResetRequest

router = APIRouter(prefix="/auth", tags=["Authentication"])

# In-memory сховище токенів для password reset (для продакшну — окрема таблиця + email delivery).
_reset_tokens: dict[str, str] = {}


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Користувач з таким email вже існує")

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2PasswordRequestForm використовує "username" — сюди підставляємо email
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірний email або пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=user.email)
    return Token(access_token=access_token)


@router.post("/password-reset/request")
def request_password_reset(payload: PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    # Навмисно не розкриваємо, чи існує email (запобігання user enumeration)
    if user:
        import secrets
        token = secrets.token_urlsafe(32)
        _reset_tokens[token] = user.email
        # TODO: тут має бути реальна відправка email через SMTP/SES/SendGrid
        # На даному етапі токен просто логуємо/повертаємо для дев-режиму
    return {"message": "Якщо email існує в системі, на нього надіслано інструкції для скидання пароля."}


@router.post("/password-reset/confirm")
def confirm_password_reset(token: str, new_password: str, db: Session = Depends(get_db)):
    email = _reset_tokens.pop(token, None)
    if not email:
        raise HTTPException(status_code=400, detail="Невалідний або прострочений токен")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")

    user.hashed_password = hash_password(new_password)
    db.commit()
    return {"message": "Пароль успішно оновлено"}
