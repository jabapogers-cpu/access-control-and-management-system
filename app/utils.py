IMAGE_TYPES = {"jpg": "image/jpeg", "png": "image/png"}


def fix_uid(uid: str) -> str:
    return uid.strip().upper()


def detect_image_type(data: bytes) -> str | None:
    if data.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    return None
