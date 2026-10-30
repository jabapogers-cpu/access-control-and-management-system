import uuid
from datetime import date, datetime
from typing import Literal

from sqlmodel import Field, SQLModel


AccessStatus = Literal["active", "blocked"]
AccessResult = Literal["granted", "denied"]
AccessMethod = Literal["card", "face"]


# сотрудники
class EmployeeCreate(SQLModel):
    name: str = Field(min_length=1, max_length=255)
    position: str = Field(min_length=1, max_length=255)
    hire_date: date


class EmployeeAccessUpdate(SQLModel):
    status: AccessStatus


class EmployeeRead(SQLModel):
    id: uuid.UUID
    name: str
    position: str
    status: str
    hire_date: date
    photo_s3_key: str | None = None
    created_at: datetime
    updated_at: datetime


class EmployeePage(SQLModel):
    items: list[EmployeeRead]
    total: int
    limit: int
    offset: int


# карты
class CardCreate(SQLModel):
    card_uid: str = Field(min_length=1, max_length=64)


class CardStatusUpdate(SQLModel):
    status: AccessStatus


class CardRead(SQLModel):
    id: uuid.UUID
    employee_id: uuid.UUID
    card_uid: str
    status: str
    issued_at: datetime


# турникеты и устройства
class AccessPointCreate(SQLModel):
    name: str = Field(min_length=1, max_length=255)
    location: str | None = Field(default=None, max_length=255)


class AccessPointRead(SQLModel):
    id: uuid.UUID
    name: str
    location: str | None = None


class DeviceCreate(SQLModel):
    access_point_id: uuid.UUID
    device_type: str = Field(min_length=1, max_length=64)


class DeviceCreated(SQLModel):
    id: uuid.UUID
    access_point_id: uuid.UUID
    device_type: str
    status: str
    api_key: str


# проверка доступа
class VerifyRequest(SQLModel):
    card_uid: str = Field(min_length=1, max_length=64)
    device_id: uuid.UUID


class VerifyResponse(SQLModel):
    allowed: bool
    reason: str
    employee_id: uuid.UUID | None = None


# журнал
class EventRead(SQLModel):
    id: uuid.UUID
    employee_id: uuid.UUID | None = None
    access_point_id: uuid.UUID
    method: str
    result: str
    score: float | None = None
    occurred_at: datetime


class EventPage(SQLModel):
    items: list[EventRead]
    total: int
    limit: int
    offset: int
