"""сотрудники"""
import uuid

from sqlalchemy import func
from sqlmodel import Session, col, select

from app.models import Employee


class EmployeeRepository:
    """достает и сохраняет сотрудников"""

    def __init__(self, session: Session) -> None:
        """запоминает сессию базы данных"""
        self.session = session

    def get(self, employee_id: uuid.UUID) -> Employee | None:
        """находит сотрудника по id (или возвращает none)"""
        return self.session.get(Employee, employee_id)

    def save(self, employee: Employee) -> Employee:
        """сохраняет нового или измененного сотрудника"""
        self.session.add(employee)
        self.session.commit()
        self.session.refresh(employee)
        return employee

    def search(
        self,
        name: str | None,
        position: str | None,
        status: str | None,
        limit: int,
        offset: int,
    ) -> tuple[list[Employee], int]:
        """ищет сотрудников по фильтрам, возвращает одну страницу и общее количество"""
        filters = []
        if name:
            filters.append(col(Employee.name).ilike(f"%{name}%"))
        if position:
            filters.append(col(Employee.position).ilike(f"%{position}%"))
        if status:
            filters.append(Employee.status == status)

        total = self.session.exec(select(func.count()).select_from(Employee).where(*filters)).one()
        items = self.session.exec(
            select(Employee)
            .where(*filters)
            .order_by(col(Employee.created_at), col(Employee.id))
            .offset(offset)
            .limit(limit)
        ).all()
        return list(items), total
