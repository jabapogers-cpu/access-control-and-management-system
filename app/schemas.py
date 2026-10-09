from datetime import date, datetime
from uuid import UUID

from sqlmodel import Field, SQLModel


class EmployeeCreate(SQLModel):
    full_name: str = Field(min_length=1, max_length=255)
    position: str = Field(min_length=1, max_length=255)
    hire_date: date


class EmployeeRead(SQLModel):
    id: UUID
    full_name: str
    position: str
    status: str
    hire_date: date
    photo_s3_key: str | None = None
    created_at: datetime
    updated_at: datetime