from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, status

from app.schemas import Employee, EmployeeCreate

app = FastAPI(title="СКУД", version="0.1.0")

# "База данных" недели 1: id -> сотрудник
employees_db: dict[int, Employee] = {}
next_id = 1


@app.get("/health", tags=["service"])
def health():
    return {"status": "ok"}


@app.post(
    "/api/v1/employees",
    response_model=Employee,
    status_code=status.HTTP_201_CREATED,
    tags=["employees"],
)
def create_employee(data: EmployeeCreate):
    global next_id
    now = datetime.now(timezone.utc)
    employee = Employee(
        id=next_id,
        created_at=now,
        updated_at=now,
        **data.model_dump(),
    )
    employees_db[next_id] = employee
    next_id += 1
    return employee


@app.get("/api/v1/employees", response_model=list[Employee], tags=["employees"])
def list_employees():
    return list(employees_db.values())


@app.get("/api/v1/employees/{employee_id}", response_model=Employee, tags=["employees"])
def get_employee(employee_id: int):
    employee = employees_db.get(employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    return employee
