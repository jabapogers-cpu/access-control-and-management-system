"""Подключение к базе данных Postgres."""
from collections.abc import Iterator

from sqlmodel import Session, create_engine

from app.config import settings
engine = create_engine(settings.database_url, echo=True)


def get_session() -> Iterator[Session]:
    """Дает сессию для работы с базой и закрывает ее после запроса."""
    with Session(engine) as session:
        yield session
