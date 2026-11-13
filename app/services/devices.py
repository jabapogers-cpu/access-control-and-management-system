"""логика работы с точками доступа и устройствами"""
import secrets
import uuid

from app.exceptions import AccessPointNotFound, DeviceNotFound, InvalidDeviceKey
from app.models import AccessPoint, Device
from app.repositories.access_points import AccessPointRepository
from app.repositories.devices import DeviceRepository
from app.schemas import AccessPointCreate, DeviceCreate, DeviceCreated
from app.security import hash_token


def check_device_key(devices: DeviceRepository, device_id: uuid.UUID, device_key: str | None) -> Device:
    """проверяет, что устройство есть и ключ верный, если нет, выбрасывает ошибку"""
    device = devices.get(device_id)
    if device is None:
        raise DeviceNotFound()
    if device_key is None or hash_token(device_key) != device.api_key_hash:
        raise InvalidDeviceKey()
    return device


class DeviceService:
    """создание точек доступа и устройств"""

    def __init__(self, access_points: AccessPointRepository, devices: DeviceRepository) -> None:
        """запоминает репозитории точек доступа и устройств"""
        self.access_points = access_points
        self.devices = devices

    def create_access_point(self, data: AccessPointCreate) -> AccessPoint:
        """создает точку доступа (турникет)"""
        return self.access_points.save(AccessPoint(**data.model_dump()))

    def list_access_points(self) -> list[AccessPoint]:
        """возвращает все точки доступа"""
        return self.access_points.list_all()

    def create_device(self, data: DeviceCreate) -> DeviceCreated:
        """создает устройство и выдает ему ключ (в базе хранится только хэш ключа)"""
        if self.access_points.get(data.access_point_id) is None:
            raise AccessPointNotFound()

        api_key = secrets.token_urlsafe(32)
        device = self.devices.save(
            Device(
                access_point_id=data.access_point_id,
                device_type=data.device_type,
                api_key_hash=hash_token(api_key),
            )
        )
        return DeviceCreated(
            id=device.id,
            access_point_id=device.access_point_id,
            device_type=device.device_type,
            status=device.status,
            api_key=api_key,
        )
