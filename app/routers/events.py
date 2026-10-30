"""Журнал входов"""
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlmodel import Session, col, select

from app.db import get_session
from app.models import AccessLog
from app.schemas import AccessMethod, AccessResult, EventPage

router = APIRouter(prefix="/api/v1/events", tags=["events"])


@router.get("", response_model=EventPage)
def list_events(
    employee_id: uuid.UUID | None = None,
    access_point_id: uuid.UUID | None = None,
    result: AccessResult | None = None,
    method: AccessMethod | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session),
) -> EventPage:
    """Возвращает журнал"""
    filters = []
    if employee_id:
        filters.append(AccessLog.employee_id == employee_id)
    if access_point_id:
        filters.append(AccessLog.access_point_id == access_point_id)
    if result:
        filters.append(AccessLog.result == result)
    if method:
        filters.append(AccessLog.method == method)
    if date_from:
        filters.append(AccessLog.occurred_at >= date_from)
    if date_to:
        filters.append(AccessLog.occurred_at <= date_to)

    total = session.exec(select(func.count()).select_from(AccessLog).where(*filters)).one()

    items = session.exec(
        select(AccessLog)
        .where(*filters)
        .order_by(col(AccessLog.occurred_at).desc(), col(AccessLog.id))
        .offset(offset)
        .limit(limit)
    ).all()
    return EventPage(items=items, total=total, limit=limit, offset=offset)
