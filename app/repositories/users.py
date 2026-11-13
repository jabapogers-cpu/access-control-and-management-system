"""пользователи и роли"""
import uuid

from sqlmodel import Session, select

from app.models import Role, User


class UserRepository:
    """достает и сохраняет пользователей"""

    def __init__(self, session: Session) -> None:
        """запоминает сессию базы данных"""
        self.session = session

    def get(self, user_id: uuid.UUID) -> User | None:
        """находит пользователя по id (или возвращает none)"""
        return self.session.get(User, user_id)

    def get_by_username(self, username: str) -> User | None:
        """находит пользователя по логину (или возвращает none)"""
        return self.session.exec(select(User).where(User.username == username)).first()

    def save(self, user: User) -> User:
        """сохраняет пользователя"""
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user


class RoleRepository:
    """достает и сохраняет роли"""

    def __init__(self, session: Session) -> None:
        """запоминает сессию базы данных"""
        self.session = session

    def get(self, role_id: uuid.UUID) -> Role | None:
        """находит роль по id (или возвращает none)"""
        return self.session.get(Role, role_id)

    def get_by_name(self, name: str) -> Role | None:
        """находит роль по названию (или возвращает none)"""
        return self.session.exec(select(Role).where(Role.name == name)).first()

    def list_all(self) -> list[Role]:
        """возвращает все роли"""
        return list(self.session.exec(select(Role)).all())

    def save(self, role: Role) -> Role:
        """сохраняет роль"""
        self.session.add(role)
        self.session.commit()
        self.session.refresh(role)
        return role
