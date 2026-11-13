"""логика работы с сотрудниками"""
import uuid

from app.exceptions import EmployeeNotFound
from app.models import Employee, now
from app.repositories.employees import EmployeeRepository
from app.schemas import EmployeeCreate, EmployeePage


def get_employee_or_raise(employees: EmployeeRepository, employee_id: uuid.UUID) -> Employee:
    """находит сотрудника, а если его нет, выбрасывает ошибку employeenotfound"""
    employee = employees.get(employee_id)
    if employee is None:
        raise EmployeeNotFound()
    return employee


class EmployeeService:
    """создание, поиск и блокировка сотрудников"""

    def __init__(self, employees: EmployeeRepository) -> None:
        """запоминает репозиторий сотрудников"""
        self.employees = employees

    def create(self, data: EmployeeCreate) -> Employee:
        """создает нового сотрудника"""
        employee = Employee(**data.model_dump())
        return self.employees.save(employee)

    def get(self, employee_id: uuid.UUID) -> Employee:
        """возвращает сотрудника по id"""
        return get_employee_or_raise(self.employees, employee_id)

    def search(
        self,
        name: str | None,
        position: str | None,
        status: str | None,
        limit: int,
        offset: int,
    ) -> EmployeePage:
        """возвращает страницу сотрудников с учетом фильтров"""
        items, total = self.employees.search(name, position, status, limit, offset)
        return EmployeePage(items=items, total=total, limit=limit, offset=offset)

    def set_status(self, employee_id: uuid.UUID, status: str) -> Employee:
        """блокирует или разблокирует сотрудника"""
        employee = get_employee_or_raise(self.employees, employee_id)
        employee.status = status
        employee.updated_at = now()
        return self.employees.save(employee)
