"""Пароли, токены и роли."""
import hashlib
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.config import settings

# Названия ролей. Должны совпадать со значениями в колонке roles.name!
ADMIN = "admin"
SECURITY = "security"
EMPLOYEE = "employee"

ACCESS_MINUTES = 15   # сколько живет access-токен
REFRESH_DAYS = 7      # сколько живет refresh-токен
BCRYPT_ROUNDS = 12    # сложность хэширования пароля


def hash_password(password: str) -> str:
    """Превращает пароль в хэш"""
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    return bcrypt.hashpw(password.encode(), salt).decode()


def check_password(password: str, password_hash: str) -> bool:
    """подходит ли пароль к хэшу"""
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except ValueError:
        return False


def hash_token(token: str) -> str:
    """Делает хэш SHA-256 от токена или ключа для хранения в бд"""
    return hashlib.sha256(token.encode()).hexdigest()


def create_access_token(user_id: uuid.UUID, minutes: int = ACCESS_MINUTES) -> str:
    """Создает JWT токен."""
    expires = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    payload = {"sub": str(user_id), "type": "access", "exp": expires}
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def decode_access_token(token: str) -> uuid.UUID | None:
    """Проверяет токен и возвращает id пользователя"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        if payload.get("type") != "access":
            return None
        return uuid.UUID(payload["sub"])
    except (jwt.PyJWTError, ValueError, KeyError):
        return None


def is_expired(moment: datetime) -> bool:
    """контроль времени"""
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment < datetime.now(timezone.utc)
