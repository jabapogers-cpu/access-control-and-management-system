from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import text
from sqlmodel import Session, select

from app.db import get_session
from app.models import Employee
from app.schemas import EmployeeCreate, EmployeeRead
from uuid import UUID

app = FastAPI(title="СКУД", version="0.2.0")


@app.get("/health", tags=["service"])
def health():
    return {"status": "ok"}


@app.get("/health/db", tags=["service"])
def health_db(session: Session = Depends(get_session)):
    session.exec(text("SELECT 1"))
    return {"db": "ok"}


@app.post(
    "/api/v1/employees",
    response_model=EmployeeRead,
    status_code=status.HTTP_201_CREATED,
    tags=["employees"],
)
def create_employee(data: EmployeeCreate, session: Session = Depends(get_session)):
    employee = Employee(**data.model_dump())
    session.add(employee)
    session.commit()
    session.refresh(employee)
    return employee


@app.get("/api/v1/employees", response_model=list[EmployeeRead], tags=["employees"])
def list_employees(session: Session = Depends(get_session)):
    return session.exec(select(Employee).order_by(Employee.id)).all()


@app.get("/api/v1/employees/{employee_id}", response_model=EmployeeRead, tags=["employees"])
def get_employee(employee_id: UUID, session: Session = Depends(get_session)):
    employee = session.get(Employee, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    return employee
