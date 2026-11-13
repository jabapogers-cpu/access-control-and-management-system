"""логика входа, токенов и ролей"""
import secrets
from datetime import timedelta

from app.exceptions import (
    Forbidden,
    InvalidAccessToken,
    InvalidCredentials,
    InvalidRefreshToken,
)
from app.models import RefreshToken, User, now
from app.repositories.refresh_tokens import RefreshTokenRepository
from app.repositories.users import RoleRepository, UserRepository
from app.schemas import AccessTokenResponse, TokenResponse
from app.security import (
    REFRESH_DAYS,
    check_password,
    create_access_token,
    decode_access_token,
    hash_token,
    is_expired,
)


class AuthService:
    """вход в систему, обновление токена, выход и проверка прав"""

    def __init__(
        self,
        users: UserRepository,
        roles: RoleRepository,
        tokens: RefreshTokenRepository,
    ) -> None:
        """запоминает репозитории пользователей, ролей и токенов"""
        self.users = users
        self.roles = roles
        self.tokens = tokens

    def login(self, username: str, password: str) -> TokenResponse:
        """проверяет логин и пароль и выдает access и refresh токены"""
        user = self.users.get_by_username(username)
        if user is None or not check_password(password, user.password_hash):
            raise InvalidCredentials()

        access_token = create_access_token(user.id)

        # refresh-токен случайный, в базу кладем только его хэш
        refresh_token = secrets.token_urlsafe(32)
        self.tokens.save(
            RefreshToken(
                user_id=user.id,
                token_hash=hash_token(refresh_token),
                expires_at=now() + timedelta(days=REFRESH_DAYS),
            )
        )
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    def refresh(self, refresh_token: str) -> AccessTokenResponse:
        """по refresh-токену выдает новый access-токен"""
        token = self.tokens.get_by_hash(hash_token(refresh_token))
        if token is None or token.revoked_at is not None or is_expired(token.expires_at):
            raise InvalidRefreshToken()

        user = self.users.get(token.user_id)
        if user is None:
            raise InvalidRefreshToken()

        return AccessTokenResponse(access_token=create_access_token(user.id))

    def logout(self, refresh_token: str) -> None:
        """отзывает refresh-токен (выход из системы)"""
        token = self.tokens.get_by_hash(hash_token(refresh_token))
        if token is not None and token.revoked_at is None:
            token.revoked_at = now()
            self.tokens.save(token)

    def get_user_from_access_token(self, access_token: str) -> User:
        """по access-токену находит пользователя, если токен плохой, выбрасывает ошибку"""
        user_id = decode_access_token(access_token)
        if user_id is None:
            raise InvalidAccessToken()

        user = self.users.get(user_id)
        if user is None:
            raise InvalidAccessToken()
        return user

    def check_role(self, user: User, allowed_roles: tuple[str, ...]) -> None:
        """проверяет, что роль пользователя входит в список разрешенных"""
        role = self.roles.get(user.role_id)
        if role is None or role.name not in allowed_roles:
            raise Forbidden()

    def get_role_name(self, user: User) -> str:
        """возвращает название роли пользователя"""
        role = self.roles.get(user.role_id)
        return role.name if role else ""
