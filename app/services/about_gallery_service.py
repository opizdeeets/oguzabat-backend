from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import List, Optional
from fastapi import UploadFile

from app.models.models import AboutGallery
from app.schemas.schemas import AboutGalleryCreate, AboutGalleryUpdate
from app.core.uploads import save_uploaded_file, delete_uploaded_file, replace_uploaded_file

# ---------------- CREATE ----------------
async def create_image(
    db: AsyncSession,
    about_gallery_in: AboutGalleryCreate,
    file: Optional[UploadFile] = None
) -> AboutGallery:
    try:
        file_path = await save_uploaded_file(file, sub_dir="about_gallery") if file else None
        db_obj = AboutGallery(**about_gallery_in.dict())
        if file_path:
            db_obj.image_path = file_path

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    except IntegrityError:
        await db.rollback()
        raise
    except SQLAlchemyError:
        await db.rollback()
        raise


# ---------------- READ ONE ----------------
async def get_image(db: AsyncSession, about_gallery_id: int) -> Optional[AboutGallery]:
    try:
        result = await db.execute(select(AboutGallery).where(AboutGallery.id == about_gallery_id))
        return result.scalars().first()
    except SQLAlchemyError:
        raise


# ---------------- READ ALL ----------------
async def get_images(db: AsyncSession, sort: str = "order_asc") -> List[AboutGallery]:
    try:
        stmt = select(AboutGallery)
        stmt = stmt.order_by(AboutGallery.order.desc() if sort == "order_desc" else AboutGallery.order.asc())
        result = await db.execute(stmt)
        return result.scalars().all()
    except SQLAlchemyError:
        raise


# ---------------- UPDATE ----------------
async def update_image(
    db: AsyncSession,
    about_gallery_id: int,
    about_gallery_in: AboutGalleryUpdate,
    new_file: Optional[UploadFile] = None
) -> Optional[AboutGallery]:
    try:
        result = await db.execute(select(AboutGallery).where(AboutGallery.id == about_gallery_id))
        db_obj = result.scalars().first()
        if not db_obj:
            return None

        update_data = about_gallery_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        # Если передан новый файл, заменяем старый
        if new_file:
            db_obj.image_path = await replace_uploaded_file(db_obj.image_path, new_file, sub_dir="about_gallery")

        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    except IntegrityError:
        await db.rollback()
        raise
    except SQLAlchemyError:
        await db.rollback()
        raise


# ---------------- DELETE ----------------
async def delete_image(db: AsyncSession, about_gallery_id: int) -> bool:
    try:
        result = await db.execute(select(AboutGallery).where(AboutGallery.id == about_gallery_id))
        db_obj = result.scalars().first()
        if not db_obj:
            return False

        # Удаляем файл с диска
        if db_obj.image_path:
            await delete_uploaded_file(db_obj.image_path)

        await db.delete(db_obj)
        await db.commit()
        return True

    except SQLAlchemyError:
        await db.rollback()
        raise
