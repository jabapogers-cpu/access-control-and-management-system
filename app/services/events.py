"""логика журнала проходов"""
import uuid
from datetime import datetime

from app.repositories.access_logs import AccessLogRepository
from app.schemas import EventPage


class EventService:
    """просмотр журнала проходов"""

    def __init__(self, logs: AccessLogRepository) -> None:
        """запоминает репозиторий журнала"""
        self.logs = logs

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
    ) -> EventPage:
        """возвращает страницу журнала с учетом фильтров"""
        items, total = self.logs.search(
            employee_id, access_point_id, result, method, date_from, date_to, limit, offset
        )
        return EventPage(items=items, total=total, limit=limit, offset=offset)
