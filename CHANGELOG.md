# Прогресс

## [3.0] JWT, роли, ключ устройства, Загрузка фото сотрудников в MinIO
- добавлен JWT для безопасности
- Эндпоинты POST /auth/login, POST /auth/refresh, POST /auth/logout, GET /auth/me
- Роли: администратор, сотрудник безопасности, обычный пользователь
- Проверка ключа устройства в /access/verify


## [2.0] Фильтры, блокировка доступа, RFID-карты, точки доступа, устройства, `/access/verify`, журнал `/events`
- Список сотрудников с фильтрами
- PATCH /employees/{id}/access: блокировка и разблокировка сотрудника.
- диаграммы UML
- поле full_name переименовано
- Привязка и блокировка карт: POST /employees/{id}/cards, GET /employees/{id}/cards, PATCH /cards/{card_uid}
- Точки доступа и устройства: POST и GET /access-points, POST /devices
- Проверка прохода по карте POST /access/verify, каждая попытка пишется в access_logs
- Журнал GET /events с фильтрами

## [1.0] FastAPI, /health, создание и чтение сотрудников, Postgres:
- эндпоинты:
  служебные /health и /health/db
  post и get /api/v1/employees и /api/v1/employees/{id}\
  gitignore
- подключение к postgres
