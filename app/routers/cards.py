"""Эндпоинты для RFID-карт"""
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, col, select

from app.db import get_session
from app.models import Employee, RfidCard
from app.schemas import CardCreate, CardRead, CardStatusUpdate
from app.utils import fix_uid

router = APIRouter(prefix="/api/v1", tags=["cards"])


@router.post("/employees/{employee_id}/cards", response_model=CardRead, status_code=201)
def bind_card(
    employee_id: uuid.UUID,
    data: CardCreate,
    session: Session = Depends(get_session),
) -> RfidCard:

    card_uid = fix_uid(data.card_uid)
    if card_uid == "":
        raise HTTPException(status_code=422, detail="UID карты не может быть пустым")

    employee = session.get(Employee, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")

    old_card = session.exec(select(RfidCard).where(RfidCard.card_uid == card_uid)).first()
    if old_card is not None:
        raise HTTPException(status_code=409, detail="Эта карта уже привязана")

    card = RfidCard(employee_id=employee_id, card_uid=card_uid)
    session.add(card)
    session.commit()
    session.refresh(card)
    return card


@router.get("/employees/{employee_id}/cards", response_model=list[CardRead])
def list_employee_cards(
    employee_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> list[RfidCard]:


    employee = session.get(Employee, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")

    cards = session.exec(
        select(RfidCard).where(RfidCard.employee_id == employee_id).order_by(col(RfidCard.issued_at))
    ).all()
    return list(cards)


@router.patch("/cards/{card_uid}", response_model=CardRead)
def update_card_status(
    card_uid: str,
    data: CardStatusUpdate,
    session: Session = Depends(get_session),
) -> RfidCard:


    card = session.exec(select(RfidCard).where(RfidCard.card_uid == fix_uid(card_uid))).first()
    if card is None:
        raise HTTPException(status_code=404, detail="Карта не найдена")

    card.status = data.status
    session.add(card)
    session.commit()
    session.refresh(card)
    return card
