"""Эндпоинты для работы с сотрудниками"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlmodel import Session, col, select

from app.db import get_session
from app.models import Employee, now
from app.schemas import (
    AccessStatus,
    EmployeeAccessUpdate,
    EmployeeCreate,
    EmployeePage,
    EmployeeRead,
)

router = APIRouter(prefix="/api/v1/employees", tags=["employees"])


@router.post("", response_model=EmployeeRead, status_code=201)
def create_employee(data: EmployeeCreate, session: Session = Depends(get_session)) -> Employee:
    """Создает нового сотрудника"""
    employee = Employee(**data.model_dump())
    session.add(employee)
    session.commit()
    session.refresh(employee)
    return employee


@router.get("", response_model=EmployeePage)
def list_employees(
    name: str | None = None,
    position: str | None = None,
    status: AccessStatus | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session),
) -> EmployeePage:
    """Возвращает список сотрудников"""
    filters = []
    if name:
        filters.append(col(Employee.name).ilike(f"%{name}%"))
    if position:
        filters.append(col(Employee.position).ilike(f"%{position}%"))
    if status:
        filters.append(Employee.status == status)


    total = session.exec(select(func.count()).select_from(Employee).where(*filters)).one()


    items = session.exec(
        select(Employee)
        .where(*filters)
        .order_by(col(Employee.created_at), col(Employee.id))
        .offset(offset)
        .limit(limit)
    ).all()
    return EmployeePage(items=items, total=total, limit=limit, offset=offset)


@router.get("/{employee_id}", response_model=EmployeeRead)
def get_employee(employee_id: uuid.UUID, session: Session = Depends(get_session)) -> Employee:
    """Возвращает одного сотрудника"""
    employee = session.get(Employee, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    return employee


@router.patch("/{employee_id}/access", response_model=EmployeeRead)
def update_access(
    employee_id: uuid.UUID,
    data: EmployeeAccessUpdate,
    session: Session = Depends(get_session),
) -> Employee:
    """Блокирует или разблокирует сотрудника"""
    employee = session.get(Employee, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")

    employee.status = data.status
    employee.updated_at = now()
    session.add(employee)
    session.commit()
    session.refresh(employee)
    return employee
