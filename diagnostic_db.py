"""
Скрипт диагностики базы данных для проекта oguzabat.
Проверяет:
1. Подключение к базе
2. Существование таблиц
3. Наличие ключевых колонок
4. Выполняет SELECT 1 для проверки работы
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import inspect, select
from sqlalchemy.orm import sessionmaker
from app.core.db import Base  # ваши модели

# ---------------- Конфигурация ----------------
DATABASE_URL = "postgresql+asyncpg://oguzabat_admin:oguzabat@localhost:5432/oguzabat_db"

# Создаём асинхронный движок SQLAlchemy
engine = create_async_engine(DATABASE_URL, echo=True)  
# echo=True → вывод всех SQL запросов, полезно для диагностики

# Асинхронная сессия
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def check_connection():
    """
    Проверка соединения с базой
    """
    try:
        async with engine.connect() as conn:
            result = await conn.execute(select(1))
            print("✅ Соединение с БД установлено, test query result:", result.scalar())
    except Exception as e:
        print("❌ Ошибка соединения с БД:", e)

async def check_tables():
    """
    Проверка наличия всех таблиц, определённых в моделях Base
    """
    async with AsyncSessionLocal() as session:
        inspector = inspect(session.bind)  # инспектор схемы
        tables = inspector.get_table_names()
        print("Найдены таблицы в базе:", tables)
        model_tables = [table.__tablename__ for table in Base.__subclasses__()]
        print("Таблицы по моделям:", model_tables)

        # Проверяем каждую таблицу модели
        for table_name in model_tables:
            if table_name in tables:
                print(f"✅ Таблица '{table_name}' существует")
                # Проверка колонок
                columns = [col["name"] for col in inspector.get_columns(table_name)]
                print(f"   Колонки: {columns}")
            else:
                print(f"❌ Таблица '{table_name}' отсутствует!")

async def main():
    await check_connection()
    await check_tables()

if __name__ == "__main__":
    asyncio.run(main())
