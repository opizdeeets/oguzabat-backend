from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import List, Optional

from app.models.models import Partner
from app.schemas.schemas import PartnerCreate, PartnerUpdate
from app.core.uploads import save_uploaded_file, delete_uploaded_file

# ---------------- CREATE ----------------
async def create_partner(
    db: AsyncSession,
    partner_in: PartnerCreate,
    logo: Optional["UploadFile"] = None
) -> Partner:
    """
    Создаёт партнёра с возможной загрузкой логотипа.
    """
    try:
        logo_path = None
        if logo:
            logo_path = await save_uploaded_file(logo, sub_dir="partners")

        db_partner = Partner(**partner_in.dict(), logo_path=logo_path or "")
        db.add(db_partner)
        await db.commit()
        await db.refresh(db_partner)
        return db_partner

    except IntegrityError:
        await db.rollback()
        raise
    except SQLAlchemyError:
        await db.rollback()
        raise


# ---------------- READ one ----------------
async def get_partner(db: AsyncSession, partner_id: int) -> Optional[Partner]:
    try:
        result = await db.execute(select(Partner).where(Partner.id == partner_id))
        return result.scalars().first()
    except SQLAlchemyError:
        raise


# ---------------- READ all ----------------
async def get_partners(db: AsyncSession, tags: Optional[List[str]] = None) -> List[Partner]:
    try:
        stmt = select(Partner)
        if tags:
            stmt = stmt.where(Partner.tags.overlap(tags))
        result = await db.execute(stmt)
        return result.scalars().all()
    except SQLAlchemyError:
        raise


# ---------------- UPDATE ----------------
async def update_partner(
    db: AsyncSession,
    partner_id: int,
    partner_in: PartnerUpdate,
    logo: Optional["UploadFile"] = None
) -> Optional[Partner]:
    """
    Обновляет партнёра, при необходимости заменяет логотип.
    """
    try:
        result = await db.execute(select(Partner).where(Partner.id == partner_id))
        db_partner = result.scalars().first()
        if not db_partner:
            return None

        update_data = partner_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_partner, field, value)

        # Логотип
        if logo:
            if db_partner.logo_path:
                await delete_uploaded_file(db_partner.logo_path)
            db_partner.logo_path = await save_uploaded_file(logo, sub_dir="partners")

        await db.commit()
        await db.refresh(db_partner)
        return db_partner

    except IntegrityError:
        await db.rollback()
        raise
    except SQLAlchemyError:
        await db.rollback()
        raise


# ---------------- DELETE ----------------
async def delete_partner(db: AsyncSession, partner_id: int) -> bool:
    """
    Удаляет партнёра и его логотип с диска.
    """
    try:
        result = await db.execute(select(Partner).where(Partner.id == partner_id))
        db_partner = result.scalars().first()
        if not db_partner:
            return False

        if db_partner.logo_path:
            await delete_uploaded_file(db_partner.logo_path)

        await db.delete(db_partner)
        await db.commit()
        return True

    except SQLAlchemyError:
        await db.rollback()
        raise
