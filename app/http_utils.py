"""вспомогательные функции для http-слоя"""
from fastapi import UploadFile

from app.exceptions import FileTooLarge

MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5 мб


def read_upload(file: UploadFile) -> bytes:
    """читает загруженный файл, а если он больше 5 мб, выбрасывает ошибку"""
    data = file.file.read(MAX_IMAGE_BYTES + 1)
    if len(data) > MAX_IMAGE_BYTES:
        raise FileTooLarge()
    return data
