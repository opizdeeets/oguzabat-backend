from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, UploadFile
from typing import List, Optional

from app.models.models import Application, ApplicationFile
from app.core.uploads import save_uploaded_file, delete_uploaded_file

# ---------------- CREATE ----------------
async def create_application(
    db: AsyncSession,
    data: dict,
    files: Optional[List[UploadFile]] = None
) -> Application:
    """
    Создаёт отклик с возможностью загружать файлы (изображения/PDF).
    Возвращает объект с полностью загруженными relationships.
    """
    try:
        file_objs = []
        if files:
            if not isinstance(files, list):
                files = [files]

            for file in files:
                # Сохраняем файл в папку 'applications'
                url = await save_uploaded_file(file, sub_dir="applications")
                file_objs.append(ApplicationFile(file_url=url))

        # Создаём объект и добавляем в сессию
        app_obj = Application(**data, files=file_objs)
        db.add(app_obj)
        await db.commit()

        # Загружаем объект полностью с relationships
        stmt = select(Application).where(Application.id == app_obj.id).options(
            selectinload(Application.files),
            selectinload(Application.vacancy)
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    except Exception:
        await db.rollback()
        raise

# ---------------- READ ALL ----------------
async def get_applications(db: AsyncSession, vacancy_id: Optional[int] = None) -> List[Application]:
    """
    Возвращает список откликов с полностью загруженными файлами и vacancy.
    """
    try:
        stmt = select(Application).options(
            selectinload(Application.files),
            selectinload(Application.vacancy)
        )
        if vacancy_id:
            stmt = stmt.where(Application.vacancy_id == vacancy_id)

        result = await db.execute(stmt)
        return result.scalars().all()
    except Exception:
        raise

# ---------------- READ ONE ----------------
async def get_application(db: AsyncSession, application_id: int) -> Optional[Application]:
    """
    Возвращает один отклик с files и vacancy.
    """
    stmt = select(Application).where(Application.id == application_id).options(
        selectinload(Application.files),
        selectinload(Application.vacancy)
    )
    result = await db.execute(stmt)
    return result.scalars().first()

# ---------------- UPDATE ----------------
async def update_application(
    db: AsyncSession,
    application_id: int,
    update_data: dict,
    new_files: Optional[List[UploadFile]] = None
) -> Application:
    """
    Обновляет поля отклика и добавляет новые файлы при необходимости.
    Возвращает объект с загруженными relationships.
    """
    # Загружаем текущий объект
    result = await db.execute(
        select(Application).where(Application.id == application_id).options(
            selectinload(Application.files)
        )
    )
    app_obj = result.scalars().first()
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")

    # Обновляем поля
    for k, v in update_data.items():
        if v is not None:
            setattr(app_obj, k, v)

    # Обрабатываем новые файлы
    if new_files:
        if not isinstance(new_files, list):
            new_files = [new_files]
        for file in new_files:
            url = await save_uploaded_file(file, sub_dir="applications")
            app_obj.files.append(ApplicationFile(file_url=url))

    await db.commit()

    # Повторно загружаем объект с relationships
    stmt = select(Application).where(Application.id == app_obj.id).options(
        selectinload(Application.files),
        selectinload(Application.vacancy)
    )
    result = await db.execute(stmt)
    return result.scalars().first()

# ---------------- DELETE ----------------
async def delete_application(db: AsyncSession, application_id: int) -> bool:
    """
    Удаляет отклик и все прикреплённые файлы.
    """
    result = await db.execute(
        select(Application).where(Application.id == application_id).options(
            selectinload(Application.files)
        )
    )
    app_obj = result.scalars().first()
    if not app_obj:
        return False

    # Удаляем файлы с диска
    for f in app_obj.files:
        await delete_uploaded_file(f.file_url)

    await db.delete(app_obj)
    await db.commit()
    return True
