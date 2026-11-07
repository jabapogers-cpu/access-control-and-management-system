"""Модели таблиц"""
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
    """Таблица RFID-карт"""
    __tablename__ = "rfid_cards"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    employee_id: uuid.UUID = Field(foreign_key="employees.id")
    card_uid: str = Field(unique=True)
    status: str = "active"
    issued_at: datetime = Field(default_factory=now)


class AccessPoint(SQLModel, table=True):
    """Таблица точек доступа"""
    __tablename__ = "access_points"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    location: str | None = None


class Device(SQLModel, table=True):
    """Таблица устройств"""
    __tablename__ = "devices"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    access_point_id: uuid.UUID = Field(foreign_key="access_points.id")
    device_type: str
    api_key_hash: str
    last_seen_at: datetime | None = None
    status: str = "active"


class AccessLog(SQLModel, table=True):
    """Таблица журнала проходов"""
    __tablename__ = "access_logs"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    employee_id: uuid.UUID | None = Field(default=None, foreign_key="employees.id")
    access_point_id: uuid.UUID = Field(foreign_key="access_points.id")
    method: str   # card или face
    result: str   # granted или denied
    score: float | None = None
    occurred_at: datetime = Field(default_factory=now)


class Role(SQLModel, table=True):
    """Таблица ролей"""
    __tablename__ = "roles"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(unique=True)


class User(SQLModel, table=True):
    """Таблица учетных записей для входа в систему"""
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(unique=True)
    password_hash: str
    role_id: uuid.UUID = Field(foreign_key="roles.id")
    employee_id: uuid.UUID | None = Field(default=None, foreign_key="employees.id")


class RefreshToken(SQLModel, table=True):
    """Таблица refresh-токенов"""
    __tablename__ = "refresh_tokens"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    token_hash: str
    expires_at: datetime
    revoked_at: datetime | None = None
    created_at: datetime = Field(default_factory=now)
