"""Главный файл приложения."""
from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlmodel import Session

from app.db import get_session
from app.routers import access, cards, devices, employees, events

app = FastAPI(title="СКУД", version="0.5.0")

app.include_router(employees.router)
app.include_router(cards.router)
app.include_router(devices.router)
app.include_router(access.router)
app.include_router(events.router)


@app.get("/health", tags=["service"])
def health() -> dict[str, str]:
    """проверка что сервер работает."""
    return {"status": "ok"}


@app.get("/health/db", tags=["service"])
def health_db(session: Session = Depends(get_session)) -> dict[str, str]:
    """проверка подключения к бд"""
    session.exec(text("SELECT 1"))
    return {"db": "ok"}
