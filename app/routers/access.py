"""Проверка доступа (сюда обращается турникет)."""
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlmodel import Session, select

from app.db import get_session
from app.models import AccessLog, Device, Employee, RfidCard
from app.schemas import VerifyRequest, VerifyResponse
from app.security import hash_token
from app.utils import fix_uid

router = APIRouter(prefix="/api/v1/access", tags=["access"])


@router.post("/verify", response_model=VerifyResponse)
def verify_card(
    data: VerifyRequest,
    x_device_key: str | None = Header(default=None),
    session: Session = Depends(get_session),
) -> VerifyResponse:
    """Проверяет карту и решает, пускать ли сотрудника. Нужен ключ устройства в заголовке X-Device-Key."""
    device = session.get(Device, data.device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="Устройство не найдено")

    # ключ устройства сравниваем по хэшу
    if x_device_key is None or hash_token(x_device_key) != device.api_key_hash:
        raise HTTPException(status_code=401, detail="Неверный ключ устройства")

    card_uid = fix_uid(data.card_uid)
    card = session.exec(select(RfidCard).where(RfidCard.card_uid == card_uid)).first()

    employee = None
    if card is not None:
        employee = session.get(Employee, card.employee_id)

    # решаем, пускать или нет
    if card is None:
        allowed = False
        reason = "unknown_card"
    elif card.status != "active":
        allowed = False
        reason = "card_blocked"
    elif employee is None or employee.status != "active":
        allowed = False
        reason = "employee_blocked"
    else:
        allowed = True
        reason = "ok"

    if allowed:
        result = "granted"
    else:
        result = "denied"

    # записываем попытку в журнал
    employee_id = employee.id if employee else None
    log = AccessLog(
        employee_id=employee_id,
        access_point_id=device.access_point_id,
        method="card",
        result=result,
    )
    session.add(log)
    session.commit()

    return VerifyResponse(allowed=allowed, reason=reason, employee_id=employee_id)
