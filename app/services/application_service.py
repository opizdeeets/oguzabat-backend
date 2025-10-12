from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, UploadFile
from typing import List, Optional
from datetime import datetime

from app.schemas.schemas import ApplicationCreate
from app.models.models import Application, ApplicationFile
from app.core.uploads import save_uploaded_file, delete_uploaded_file


# ---------------- CREATE ----------------
async def create_application(
    db: AsyncSession,
    application_in: ApplicationCreate,
    files: Optional[List[UploadFile]] = None
) -> Application:
    """
    Создаёт заявку (Application) с опциональными файлами.
    Дата создания берётся автоматически, явно задаём UTC now.
    """
    try:
        file_objs: List[ApplicationFile] = []

        if files:
            if not isinstance(files, list):
                files = [files]
            for file in files:
                file_url = await save_uploaded_file(file, sub_dir="applications")
                file_objs.append(ApplicationFile(file_url=file_url))

        app_obj = Application(
            **application_in.dict(),
            files=file_objs,
            created_at=datetime.utcnow()
        )
        db.add(app_obj)
        await db.commit()

        # Используем selectinload для связанных объектов
        result = await db.execute(
            select(Application)
            .where(Application.id == app_obj.id)
            .options(
                selectinload(Application.files),
                selectinload(Application.vacancy)
            )
        )
        app_obj = result.scalars().first()
        return app_obj

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


# ---------------- READ ALL ----------------
async def get_applications(
    db: AsyncSession,
    vacancy_id: Optional[int] = None
) -> List[Application]:
    stmt = (
        select(Application)
        .options(
            selectinload(Application.files),
            selectinload(Application.vacancy)
        )
        .order_by(Application.created_at.desc())
    )
    if vacancy_id:
        stmt = stmt.where(Application.vacancy_id == vacancy_id)

    result = await db.execute(stmt)
    return result.scalars().unique().all()


# ---------------- READ ONE ----------------
async def get_application(
    db: AsyncSession,
    application_id: int
) -> Application:
    stmt = (
        select(Application)
        .where(Application.id == application_id)
        .options(
            selectinload(Application.files),
            selectinload(Application.vacancy)
        )
    )
    result = await db.execute(stmt)
    app_obj = result.scalars().first()
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")
    return app_obj


# ---------------- UPDATE ----------------
async def update_application(
    db: AsyncSession,
    application_id: int,
    update_data: dict,
    new_files: Optional[List[UploadFile]] = None
) -> Application:
    result = await db.execute(
        select(Application)
        .where(Application.id == application_id)
        .options(selectinload(Application.files))
    )
    app_obj = result.scalars().first()
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")

    for key, value in update_data.items():
        if value is not None:
            setattr(app_obj, key, value)

    if new_files:
        if not isinstance(new_files, list):
            new_files = [new_files]
        for file in new_files:
            file_url = await save_uploaded_file(file, sub_dir="applications")
            app_obj.files.append(ApplicationFile(file_url=file_url))

    try:
        await db.commit()
        # Заново загружаем связи
        result = await db.execute(
            select(Application)
            .where(Application.id == application_id)
            .options(
                selectinload(Application.files),
                selectinload(Application.vacancy)
            )
        )
        app_obj = result.scalars().first()
        return app_obj

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Update failed: {e}")


# ---------------- DELETE ----------------
async def delete_application(
    db: AsyncSession,
    application_id: int
) -> bool:
    result = await db.execute(
        select(Application)
        .where(Application.id == application_id)
        .options(selectinload(Application.files))
    )
    app_obj = result.scalars().first()
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")

    # Удаляем файлы физически
    for file in app_obj.files:
        await delete_uploaded_file(file.file_url)

    try:
        await db.delete(app_obj)
        await db.commit()
        return True

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Delete failed: {e}")
