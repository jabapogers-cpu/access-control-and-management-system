"""Работа с хранилищем фотографий"""
import io

from minio import Minio

from app.config import settings


class PhotoStorage:
    def __init__(self) -> None:
        """установка соединения при первом запросе"""
        self.bucket = settings.s3_bucket
        self.client = Minio(
            settings.s3_endpoint,
            access_key=settings.s3_access_key,
            secret_key=settings.s3_secret_key,
            secure=settings.s3_secure,
        )

    def upload(self, key: str, data: bytes, content_type: str) -> None:
        """Загружает файл в хранилище"""
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)
        self.client.put_object(
            self.bucket,
            key,
            io.BytesIO(data),
            length=len(data),
            content_type=content_type,
        )

    def download(self, key: str) -> bytes:
        """Скачивает файл из хранилища и возвращает его содержимое"""
        response = self.client.get_object(self.bucket, key)
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()

    def delete(self, key: str) -> None:
        """Удаляет файл из хранилища"""
        self.client.remove_object(self.bucket, key)


def get_storage() -> PhotoStorage:
    return PhotoStorage()
