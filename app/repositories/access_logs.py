"""журнал проходов"""
import uuid
from datetime import datetime

from sqlalchemy import func
from sqlmodel import Session, col, select

from app.models import AccessLog


class AccessLogRepository:
    """записывает события в журнал и ищет их"""

    def __init__(self, session: Session) -> None:
        """запоминает сессию базы данных"""
        self.session = session

    def add(
        self,
        employee_id: uuid.UUID | None,
        access_point_id: uuid.UUID,
        method: str,
        result: str,
        score: float | None = None,
    ) -> None:
        """добавляет запись о попытке прохода"""
        log = AccessLog(
            employee_id=employee_id,
            access_point_id=access_point_id,
            method=method,
            result=result,
            score=score,
        )
        self.session.add(log)
        self.session.commit()

    def search(
        self,
        employee_id: uuid.UUID | None,
        access_point_id: uuid.UUID | None,
        result: str | None,
        method: str | None,
        date_from: datetime | None,
        date_to: datetime | None,
        limit: int,
        offset: int,
    ) -> tuple[list[AccessLog], int]:
        """ищет события по фильтрам (новые сверху), возвращает страницу и общее количество"""
        filters = []
        if employee_id:
            filters.append(AccessLog.employee_id == employee_id)
        if access_point_id:
            filters.append(AccessLog.access_point_id == access_point_id)
        if result:
            filters.append(AccessLog.result == result)
        if method:
            filters.append(AccessLog.method == method)
        if date_from:
            filters.append(AccessLog.occurred_at >= date_from)
        if date_to:
            filters.append(AccessLog.occurred_at <= date_to)

        total = self.session.exec(select(func.count()).select_from(AccessLog).where(*filters)).one()
        items = self.session.exec(
            select(AccessLog)
            .where(*filters)
            .order_by(col(AccessLog.occurred_at).desc(), col(AccessLog.id))
            .offset(offset)
            .limit(limit)
        ).all()
        return list(items), total
