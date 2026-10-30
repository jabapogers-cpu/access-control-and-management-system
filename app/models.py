import uuid
from datetime import date, datetime, timezone

from sqlmodel import Field, SQLModel


def now() -> datetime:
    """возвращает текущее время"""
    return datetime.now(timezone.utc)


class Employee(SQLModel, table=True):
    """таблица сотрудников"""
    __tablename__ = "employees"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    position: str
    status: str = "active"
    hire_date: date
    photo_s3_key: str | None = None
    created_at: datetime = Field(default_factory=now)
    updated_at: datetime = Field(default_factory=now)


class RfidCard(SQLModel, table=True):
    """таблица RFID-карт."""
    __tablename__ = "rfid_cards"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    employee_id: uuid.UUID = Field(foreign_key="employees.id")
    card_uid: str = Field(unique=True)
    status: str = "active"
    issued_at: datetime = Field(default_factory=now)


class AccessPoint(SQLModel, table=True):
    """таблица турникетов"""
    __tablename__ = "access_points"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    location: str | None = None


class Device(SQLModel, table=True):
    """таблица устройств пропуска"""
    __tablename__ = "devices"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    access_point_id: uuid.UUID = Field(foreign_key="access_points.id")
    device_type: str
    api_key_hash: str
    last_seen_at: datetime | None = None
    status: str = "active"


class AccessLog(SQLModel, table=True):
    """журнал проходов"""
    __tablename__ = "access_logs"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    employee_id: uuid.UUID | None = Field(default=None, foreign_key="employees.id")
    access_point_id: uuid.UUID = Field(foreign_key="access_points.id")
    method: str   # card или face
    result: str   # granted или denied
    score: float | None = None
    occurred_at: datetime = Field(default_factory=now)
