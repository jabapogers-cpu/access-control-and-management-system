"""Эндпоинты для точек доступа и устройств"""
import hashlib
import secrets

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, col, select

from app.db import get_session
from app.models import AccessPoint, Device
from app.schemas import AccessPointCreate, AccessPointRead, DeviceCreate, DeviceCreated

router = APIRouter(prefix="/api/v1", tags=["devices"])


@router.post("/access-points", response_model=AccessPointRead, status_code=201)
def create_access_point(
    data: AccessPointCreate,
    session: Session = Depends(get_session),
) -> AccessPoint:
    """создает турникет"""
    access_point = AccessPoint(**data.model_dump())
    session.add(access_point)
    session.commit()
    session.refresh(access_point)
    return access_point


@router.get("/access-points", response_model=list[AccessPointRead])
def list_access_points(session: Session = Depends(get_session)) -> list[AccessPoint]:
    """Возвращает список всех турникетов"""
    points = session.exec(select(AccessPoint).order_by(col(AccessPoint.name))).all()
    return list(points)


@router.post("/devices", response_model=DeviceCreated, status_code=201)
def create_device(data: DeviceCreate, session: Session = Depends(get_session)) -> DeviceCreated:
    """создает устройство"""
    access_point = session.get(AccessPoint, data.access_point_id)
    if access_point is None:
        raise HTTPException(status_code=404, detail="Точка доступа не найдена")

    # хэш ключа
    api_key = secrets.token_urlsafe(32)
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    device = Device(
        access_point_id=data.access_point_id,
        device_type=data.device_type,
        api_key_hash=key_hash,
    )
    session.add(device)
    session.commit()
    session.refresh(device)

    return DeviceCreated(
        id=device.id,
        access_point_id=device.access_point_id,
        device_type=device.device_type,
        status=device.status,
        api_key=api_key,
    )
