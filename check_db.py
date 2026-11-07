"""Проверка подключения и просмотр структуры БД.

Запуск (из корня проекта, с активированным .venv):
    python check_db.py
"""
from sqlalchemy import inspect, text

from app.db import engine

engine.echo = False

with engine.connect() as conn:
    print("Подключение OK:", conn.execute(text("SELECT version()")).scalar())

inspector = inspect(engine)
for table in inspector.get_table_names():
    print(f"\n{table}")
    for col in inspector.get_columns(table):
        null = "NULL" if col["nullable"] else "NOT NULL"
        default = f" default={col['default']}" if col.get("default") else ""
        print(f"   {col['name']:<22} {str(col['type']):<28} {null}{default}")
