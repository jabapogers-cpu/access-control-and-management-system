"""устройства"""
import uuid

from sqlmodel import Session

from app.models import Device


class DeviceRepository:
    """достает и сохраняет устройства"""

    def __init__(self, session: Session) -> None:
        """запоминает сессию базы данных"""
        self.session = session

    def get(self, device_id: uuid.UUID) -> Device | None:
        """находит устройство по id (или возвращает none)"""
        return self.session.get(Device, device_id)

    def save(self, device: Device) -> Device:
        """сохраняет устройство"""
        self.session.add(device)
        self.session.commit()
        self.session.refresh(device)
        return device
