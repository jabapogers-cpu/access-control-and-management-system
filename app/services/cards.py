"""логика работы с rfid-картами"""
import uuid

from app.exceptions import CardAlreadyBound, CardNotFound, EmptyCardUid
from app.models import RfidCard
from app.repositories.cards import CardRepository
from app.repositories.employees import EmployeeRepository
from app.services.employees import get_employee_or_raise
from app.utils import fix_uid


class CardService:
    """привязка и блокировка карт"""

    def __init__(self, cards: CardRepository, employees: EmployeeRepository) -> None:
        """запоминает репозитории карт и сотрудников"""
        self.cards = cards
        self.employees = employees

    def bind(self, employee_id: uuid.UUID, raw_uid: str) -> RfidCard:
        """привязывает карту к сотруднику"""
        card_uid = fix_uid(raw_uid)
        if card_uid == "":
            raise EmptyCardUid()

        get_employee_or_raise(self.employees, employee_id)

        if self.cards.get_by_uid(card_uid) is not None:
            raise CardAlreadyBound()

        return self.cards.save(RfidCard(employee_id=employee_id, card_uid=card_uid))

    def list_for_employee(self, employee_id: uuid.UUID) -> list[RfidCard]:
        """возвращает все карты сотрудника"""
        get_employee_or_raise(self.employees, employee_id)
        return self.cards.list_for_employee(employee_id)

    def set_status(self, raw_uid: str, status: str) -> RfidCard:
        """блокирует или разблокирует карту"""
        card = self.cards.get_by_uid(fix_uid(raw_uid))
        if card is None:
            raise CardNotFound()
        card.status = status
        return self.cards.save(card)
