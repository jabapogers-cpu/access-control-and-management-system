from collections.abc import Callable

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from app.db import get_session
from app.models import Role, User
from app.security import ADMIN, SECURITY, decode_access_token

bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    session: Session = Depends(get_session),
) -> User:
    """берет токен из заголовка Authorization и возвращает пользователя"""
    if credentials is None:
        raise HTTPException(status_code=401, detail="Нужна авторизация")

    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Токен недействителен или просрочен")

    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    return user


def require_roles(*allowed_roles: str) -> Callable[..., User]:
    """пускает только пользователей с указаными ролями"""

    def check(
        user: User = Depends(get_current_user),
        session: Session = Depends(get_session),
    ) -> User:
        """Проверяет роль текущего пользователя."""
        role = session.get(Role, user.role_id)
        if role is None or role.name not in allowed_roles:
            raise HTTPException(status_code=403, detail="Недостаточно прав")
        return user

    return check


admin_only = Depends(require_roles(ADMIN))
admin_or_security = Depends(require_roles(ADMIN, SECURITY))
