"""refresh токены"""
from sqlmodel import Session, select

from app.models import RefreshToken


class RefreshTokenRepository:
    """достает и сохраняет refresh-токены"""

    def __init__(self, session: Session) -> None:
        """запоминает сессию базы данных"""
        self.session = session

    def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        """находит токен по хэшу (или возвращает none)"""
        return self.session.exec(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        ).first()

    def save(self, token: RefreshToken) -> RefreshToken:
        """сохраняет новый или измененный токен"""
        self.session.add(token)
        self.session.commit()
        self.session.refresh(token)
        return token
