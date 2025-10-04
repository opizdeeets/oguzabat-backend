from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.models.models import AboutGallery
from app.schemas.schemas import AboutGalleryCreate, AboutGalleryUpdate
from typing import List, Optional

# CREATE
async def create_image(db: AsyncSession, about_gallery_in: AboutGalleryCreate) -> AboutGallery:
    try:
        db_about_gallery = AboutGallery(**about_gallery_in.dict())
        db.add(db_about_gallery)
        await db.commit()
        await db.refresh(db_about_gallery)
        return db_about_gallery
    except IntegrityError:
        await db.rollback()
        raise
    except SQLAlchemyError:
        await db.rollback()
        raise


# READ one
async def get_image(db: AsyncSession, about_gallery_id: int) -> Optional[AboutGallery]:
    try:
        result = await db.execute(select(AboutGallery).where(AboutGallery.id == about_gallery_id))
        return result.scalars().first()
    except SQLAlchemyError:
        raise


# READ all
async def get_images(db: AsyncSession, sort: str = "order_asc") -> List[AboutGallery]:
    try:
        stmt = select(AboutGallery)

        if sort == "order_desc":
            stmt = stmt.order_by(AboutGallery.order.desc())
        else:  # ВСЕ остальные случаи → order_asc
            stmt = stmt.order_by(AboutGallery.order.asc())

        result = await db.execute(stmt)
        return result.scalars().all()
    except SQLAlchemyError:
        raise


# UPDATE
async def update_image(db: AsyncSession, about_gallery_id: int, about_gallery_in: AboutGalleryUpdate) -> Optional[AboutGallery]:
    try:
        result = await db.execute(select(AboutGallery).where(AboutGallery.id == about_gallery_id))
        db_about_gallery = result.scalars().first()

        if not db_about_gallery:
            return None

        update_data = about_gallery_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_about_gallery, field, value)

        await db.commit()
        await db.refresh(db_about_gallery)
        return db_about_gallery
    except IntegrityError:
        await db.rollback()
        raise
    except SQLAlchemyError:
        await db.rollback()
        raise


# DELETE
async def delete_image(db: AsyncSession, about_gallery_id: int) -> bool:
    try:
        result = await db.execute(delete(AboutGallery).where(AboutGallery.id == about_gallery_id))  # Эффективное удаление
        await db.commit()
        return result.rowcount > 0
    except SQLAlchemyError:
        await db.rollback()
        raise