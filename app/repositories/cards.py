"""rfid-карты"""
import uuid

from sqlmodel import Session, col, select

from app.models import RfidCard


class CardRepository:
    """достает и сохраняет карты"""

    def __init__(self, session: Session) -> None:
        """запоминает сессию базы данных"""
        self.session = session

    def get_by_uid(self, card_uid: str) -> RfidCard | None:
        """находит карту по uid (или возвращает none)"""
        return self.session.exec(select(RfidCard).where(RfidCard.card_uid == card_uid)).first()

    def list_for_employee(self, employee_id: uuid.UUID) -> list[RfidCard]:
        """возвращает все карты сотрудника"""
        cards = self.session.exec(
            select(RfidCard)
            .where(RfidCard.employee_id == employee_id)
            .order_by(col(RfidCard.issued_at))
        ).all()
        return list(cards)

    def save(self, card: RfidCard) -> RfidCard:
        """сохраняет новую или измененную карту"""
        self.session.add(card)
        self.session.commit()
        self.session.refresh(card)
        return card
