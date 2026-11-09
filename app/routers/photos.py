"""Фотографии сотрудников"""
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile
from sqlmodel import Session

from app.db import get_session
from app.deps import admin_only, admin_or_security
from app.models import Employee, now
from app.schemas import EmployeeRead
from app.storage import PhotoStorage, get_storage
from app.utils import IMAGE_TYPES, detect_image_type

router = APIRouter(prefix="/api/v1/employees", tags=["photos"])

MAX_PHOTO_BYTES = 5 * 1024 * 1024  # 5 МБ


def get_employee_or_404(session: Session, employee_id: uuid.UUID) -> Employee:
    """Ищет сотрудника, а если его нет, возвращает ошибку 40."""
    employee = session.get(Employee, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    return employee


@router.post("/{employee_id}/photo", response_model=EmployeeRead, dependencies=[admin_only])
def upload_photo(
    employee_id: uuid.UUID,
    photo: UploadFile = File(...),
    session: Session = Depends(get_session),
    storage: PhotoStorage = Depends(get_storage),
) -> Employee:
    """Загружает фото сотрудника в хранилище (jpg или png, до 5 МБ)"""
    employee = get_employee_or_404(session, employee_id)

    data = photo.file.read(MAX_PHOTO_BYTES + 1)
    if len(data) > MAX_PHOTO_BYTES:
        raise HTTPException(status_code=413, detail="Файл больше 5 МБ")

    image_type = detect_image_type(data)
    if image_type is None:
        raise HTTPException(status_code=422, detail="Нужна картинка в формате jpg или png")

    key = f"employees/{employee_id}/{uuid.uuid4().hex}.{image_type}"
    try:
        storage.upload(key, data, IMAGE_TYPES[image_type])
    except Exception:
        raise HTTPException(status_code=503, detail="Хранилище фотографий недоступно")

    old_key = employee.photo_s3_key
    employee.photo_s3_key = key
    employee.updated_at = now()
    session.add(employee)
    session.commit()
    session.refresh(employee)

    if old_key:
        try:
            storage.delete(old_key)
        except Exception:
            pass
    return employee


@router.get("/{employee_id}/photo", dependencies=[admin_or_security])
def get_photo(
    employee_id: uuid.UUID,
    session: Session = Depends(get_session),
    storage: PhotoStorage = Depends(get_storage),
) -> Response:
    """Отдаёт фото сотрудника"""
    employee = get_employee_or_404(session, employee_id)
    if employee.photo_s3_key is None:
        raise HTTPException(status_code=404, detail="Фото не загружено")

    try:
        data = storage.download(employee.photo_s3_key)
    except Exception:
        raise HTTPException(status_code=503, detail="Хранилище фотографий недоступно")

    image_type = employee.photo_s3_key.rsplit(".", 1)[-1]
    return Response(content=data, media_type=IMAGE_TYPES.get(image_type, "image/jpeg"))


@router.delete("/{employee_id}/photo", response_model=EmployeeRead, dependencies=[admin_only])
def delete_photo(
    employee_id: uuid.UUID,
    session: Session = Depends(get_session),
    storage: PhotoStorage = Depends(get_storage),
) -> Employee:
    """Удаляет фото сотрудника из хранилища и очищает ссылку в базе"""
    employee = get_employee_or_404(session, employee_id)
    if employee.photo_s3_key is None:
        raise HTTPException(status_code=404, detail="Фото не загружено")

    try:
        storage.delete(employee.photo_s3_key)
    except Exception:
        raise HTTPException(status_code=503, detail="Хранилище фотографий недоступно")

    employee.photo_s3_key = None
    employee.updated_at = now()
    session.add(employee)
    session.commit()
    session.refresh(employee)
    return employee
