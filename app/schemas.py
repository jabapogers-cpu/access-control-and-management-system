from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field


class EmployeeStatus(str, Enum):
    active = "active"      # доступ разрешён
    blocked = "blocked"    # доступ заблокирован


class EmployeeCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=255, examples=["Иванов Иван Иванович"])
    position: str = Field(min_length=1, max_length=255, examples=["Инженер"])
    hire_date: date = Field(examples=["2026-09-01"])


class Employee(EmployeeCreate):
    id: int
    status: EmployeeStatus = EmployeeStatus.active
    created_at: datetime
    updated_at: datetime
