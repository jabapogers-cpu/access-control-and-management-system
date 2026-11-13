"""точки доступа"""
import uuid

from sqlmodel import Session, col, select

from app.models import AccessPoint


class AccessPointRepository:
    """достает и сохраняет точки доступа"""

    def __init__(self, session: Session) -> None:
        """запоминает сессию базы данных"""
        self.session = session

    def get(self, access_point_id: uuid.UUID) -> AccessPoint | None:
        """находит точку доступа по id (или возвращает none)"""
        return self.session.get(AccessPoint, access_point_id)

    def list_all(self) -> list[AccessPoint]:
        """возвращает все точки доступа по алфавиту"""
        points = self.session.exec(select(AccessPoint).order_by(col(AccessPoint.name))).all()
        return list(points)

    def save(self, access_point: AccessPoint) -> AccessPoint:
        """сохраняет точку доступа"""
        self.session.add(access_point)
        self.session.commit()
        self.session.refresh(access_point)
        return access_point
