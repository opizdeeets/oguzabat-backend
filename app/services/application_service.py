from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, UploadFile
from typing import List, Optional

from app.models.models import Application, ApplicationFile
from app.core.uploads import upload_company_logo, delete_upload_file

# ---------------- CREATE ----------------
async def create_application(
    db: AsyncSession,
    data: dict,
    files: Optional[List[UploadFile]] = None
) -> Application:
    """
    Создаёт отклик с возможностью загружать файлы.
    Возвращает объект с полностью загруженными relationships.
    """
    try:
        file_objs = []
        if files:
            # Если передан один файл как UploadFile, превращаем в список
            if not isinstance(files, list):
                files = [files]

            for file in files:
                print(f"application_service: saving file {file.filename}")
                url = await upload_company_logo(file)
                print(f"application_service: saved file to {url}")
                file_objs.append(ApplicationFile(file_url=url))

        # Создаём объект и добавляем в сессию
        app_obj = Application(**data, files=file_objs)
        db.add(app_obj)
        await db.commit()

        # Обновляем объект из базы, чтобы relationships были полностью загружены
        stmt = select(Application).where(Application.id == app_obj.id).options(
            selectinload(Application.files),
            selectinload(Application.vacancy)
        )
        result = await db.execute(stmt)
        app_obj = result.scalars().first()
        return app_obj

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
        applications = result.scalars().all()
        return applications

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
    result = await db.execute(
        select(Application).where(Application.id == application_id).options(
            selectinload(Application.files)
        )
    )
    app_obj = result.scalars().first()
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")

    # Обновляем поля объекта
    for k, v in update_data.items():
        if v is not None:
            setattr(app_obj, k, v)

    # Обрабатываем новые файлы
    if new_files:
        if not isinstance(new_files, list):
            new_files = [new_files]
        for f in new_files:
            url = await upload_company_logo(f)
            app_obj.files.append(ApplicationFile(file_url=url))

    await db.commit()

    # Повторно загружаем объект с files и vacancy
    stmt = select(Application).where(Application.id == app_obj.id).options(
        selectinload(Application.files),
        selectinload(Application.vacancy)
    )
    result = await db.execute(stmt)
    app_obj = result.scalars().first()
    return app_obj

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

    for f in app_obj.files:
        await delete_upload_file(f.file_url)

    await db.delete(app_obj)
    await db.commit()
    return True
