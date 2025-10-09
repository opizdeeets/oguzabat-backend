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
    file_objs = []
    if files:
        if not isinstance(files, list):
            files = [files]
        for f in files:
            url = await save_uploaded_file(f, sub_dir="applications")
            file_objs.append(ApplicationFile(file_url=url))

    app_obj = Application(**data, files=file_objs)
    db.add(app_obj)
    await db.commit()

    stmt = select(Application).where(Application.id == app_obj.id).options(
        selectinload(Application.files),
        selectinload(Application.vacancy)
    )
    result = await db.execute(stmt)
    return result.scalars().first()

# ---------------- READ ALL ----------------
async def get_applications(db: AsyncSession, vacancy_id: Optional[int] = None) -> List[Application]:
    stmt = select(Application).options(
        selectinload(Application.files),
        selectinload(Application.vacancy)
    )
    if vacancy_id:
        stmt = stmt.where(Application.vacancy_id == vacancy_id)

    result = await db.execute(stmt)
    return result.scalars().all()

# ---------------- READ ONE ----------------
async def get_application(db: AsyncSession, application_id: int) -> Optional[Application]:
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
    result = await db.execute(
        select(Application).where(Application.id == application_id).options(
            selectinload(Application.files)
        )
    )
    app_obj = result.scalars().first()
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")

    for k, v in update_data.items():
        if v is not None:
            setattr(app_obj, k, v)

    if new_files:
        if not isinstance(new_files, list):
            new_files = [new_files]
        for f in new_files:
            url = await save_uploaded_file(f, sub_dir="applications")
            app_obj.files.append(ApplicationFile(file_url=url))

    await db.commit()

    stmt = select(Application).where(Application.id == app_obj.id).options(
        selectinload(Application.files),
        selectinload(Application.vacancy)
    )
    result = await db.execute(stmt)
    return result.scalars().first()

# ---------------- DELETE ----------------
async def delete_application(db: AsyncSession, application_id: int) -> bool:
    result = await db.execute(
        select(Application).where(Application.id == application_id).options(
            selectinload(Application.files)
        )
    )
    app_obj = result.scalars().first()
    if not app_obj:
        return False

    for f in app_obj.files:
        await delete_uploaded_file(f.file_url)

    await db.delete(app_obj)
    await db.commit()
    return True
