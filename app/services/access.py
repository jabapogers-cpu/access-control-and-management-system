"""логика проверки доступа по карте"""
import uuid

from app.repositories.access_logs import AccessLogRepository
from app.repositories.cards import CardRepository
from app.repositories.devices import DeviceRepository
from app.repositories.employees import EmployeeRepository
from app.schemas import VerifyResponse
from app.services.devices import check_device_key
from app.utils import fix_uid


class AccessService:
    """решает, пускать ли сотрудника по карте"""

    def __init__(
        self,
        devices: DeviceRepository,
        cards: CardRepository,
        employees: EmployeeRepository,
        logs: AccessLogRepository,
    ) -> None:
        """запоминает репозитории, с которыми будет работать"""
        self.devices = devices
        self.cards = cards
        self.employees = employees
        self.logs = logs

    def verify_card(self, device_id: uuid.UUID, device_key: str | None, raw_uid: str) -> VerifyResponse:
        """проверяет карту и решает, пускать ли сотрудника, результат пишется в журнал"""
        device = check_device_key(self.devices, device_id, device_key)

        card = self.cards.get_by_uid(fix_uid(raw_uid))

        employee = None
        if card is not None:
            employee = self.employees.get(card.employee_id)

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

        result = "granted" if allowed else "denied"
        employee_id = employee.id if employee else None
        self.logs.add(employee_id, device.access_point_id, "card", result)

        return VerifyResponse(allowed=allowed, reason=reason, employee_id=employee_id)
