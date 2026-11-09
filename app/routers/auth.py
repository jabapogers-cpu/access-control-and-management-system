"""Вход в систему, обновление токена, выход"""
import secrets
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db import get_session
from app.deps import get_current_user
from app.models import RefreshToken, Role, User, now
from app.schemas import (
    AccessTokenResponse,
    LoginRequest,
    MeResponse,
    RefreshRequest,
    TokenResponse,
)
from app.security import (
    REFRESH_DAYS,
    check_password,
    create_access_token,
    hash_token,
    is_expired,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, session: Session = Depends(get_session)) -> TokenResponse:
    """Проверяет логин и пароль и выдает access и refresh токены"""
    user = session.exec(select(User).where(User.username == data.username)).first()
    if user is None or not check_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    access_token = create_access_token(user.id)

    # refresh-токен случайный, в базу кладём только его хэш
    refresh_token = secrets.token_urlsafe(32)
    session.add(
        RefreshToken(
            user_id=user.id,
            token_hash=hash_token(refresh_token),
            expires_at=now() + timedelta(days=REFRESH_DAYS),
        )
    )
    session.commit()

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=AccessTokenResponse)
def refresh(data: RefreshRequest, session: Session = Depends(get_session)) -> AccessTokenResponse:
    """По refresh-токену выдает новый access-токен"""
    token = session.exec(
        select(RefreshToken).where(RefreshToken.token_hash == hash_token(data.refresh_token))
    ).first()

    if token is None or token.revoked_at is not None or is_expired(token.expires_at):
        raise HTTPException(status_code=401, detail="Refresh-токен недействителен")

    user = session.get(User, token.user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="Пользователь не найден")

    return AccessTokenResponse(access_token=create_access_token(user.id))


@router.post("/logout")
def logout(data: RefreshRequest, session: Session = Depends(get_session)) -> dict[str, str]:
    """Отзывает refresh-токен (выход из системы)"""
    token = session.exec(
        select(RefreshToken).where(RefreshToken.token_hash == hash_token(data.refresh_token))
    ).first()

    if token is not None and token.revoked_at is None:
        token.revoked_at = now()
        session.add(token)
        session.commit()
    return {"status": "ok"}


@router.get("/me", response_model=MeResponse)
def me(user: User = Depends(get_current_user), session: Session = Depends(get_session)) -> MeResponse:
    """Возвращает данные текущего пользователя"""
    role = session.get(Role, user.role_id)
    role_name = role.name if role else ""
    return MeResponse(id=user.id, username=user.username, role=role_name)
