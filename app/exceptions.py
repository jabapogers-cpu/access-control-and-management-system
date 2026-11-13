"""ошибки приложения"""


class AppError(Exception):
    """базовая ошибка приложения"""
    status_code: int = 400
    detail: str = "Ошибка запроса"


class EmployeeNotFound(AppError):
    """сотрудник не найден"""
    status_code = 404
    detail = "Сотрудник не найден"


class DeviceNotFound(AppError):
    """устройство не найдено"""
    status_code = 404
    detail = "Устройство не найдено"


class InvalidDeviceKey(AppError):
    """ключ устройства не передан или неверный"""
    status_code = 401
    detail = "Неверный ключ устройства"


class BadImage(AppError):
    """файл не удалось прочитать как изображение"""
    status_code = 422
    detail = "Не удалось прочитать изображение"


class FileTooLarge(AppError):
    """файл слишком большой"""
    status_code = 413
    detail = "Файл больше 5 МБ"


class NotAuthenticated(AppError):
    """запрос без токена"""
    status_code = 401
    detail = "Нужна авторизация"


class InvalidAccessToken(AppError):
    """access-токен недействителен или просрочен"""
    status_code = 401
    detail = "Токен недействителен или просрочен"


class Forbidden(AppError):
    """у пользователя нет нужной роли"""
    status_code = 403
    detail = "Недостаточно прав"


class InvalidCredentials(AppError):
    """неверный логин или пароль"""
    status_code = 401
    detail = "Неверный логин или пароль"


class InvalidRefreshToken(AppError):
    """refresh-токен недействителен, отозван или просрочен"""
    status_code = 401
    detail = "Refresh-токен недействителен"


class CardNotFound(AppError):
    """карта не найдена"""
    status_code = 404
    detail = "Карта не найдена"


class CardAlreadyBound(AppError):
    """карта уже привязана к сотруднику"""
    status_code = 409
    detail = "Эта карта уже привязана"


class EmptyCardUid(AppError):
    """uid карты пустой"""
    status_code = 422
    detail = "UID карты не может быть пустым"


class AccessPointNotFound(AppError):
    """точка доступа не найдена"""
    status_code = 404
    detail = "Точка доступа не найдена"


class PhotoNotFound(AppError):
    """у сотрудника нет фото"""
    status_code = 404
    detail = "Фото не загружено"


class UnsupportedImage(AppError):
    """файл не jpg и не png"""
    status_code = 422
    detail = "Нужна картинка в формате jpg или png"


class StorageUnavailable(AppError):
    """хранилище фотографий не отвечает"""
    status_code = 503
    detail = "Хранилище фотографий недоступно"
