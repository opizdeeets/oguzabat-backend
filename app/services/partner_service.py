from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.models.models import Partner
from app.schemas.schemas import PartnerCreate, PartnerUpdate
from typing import List, Optional


# CREATE
async def create_partner(db: AsyncSession, partner_in: PartnerCreate) -> Partner:
    try:
        db_partner = Partner(**partner_in.dict())
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


# READ one
async def get_partner(db: AsyncSession, partner_id: int) -> Optional[Partner]:
    try:
        result = await db.execute(select(Partner).where(Partner.id == partner_id))
        return result.scalars().first()
    except SQLAlchemyError:
        raise


# READ all (БЕЗ пагинации)
async def get_partners(db: AsyncSession, tags: Optional[List[str]] = None) -> List[Partner]:
    try:
        stmt = select(Partner)

        if tags:
            stmt = stmt.where(Partner.tags.overlap(tags))

        result = await db.execute(stmt)
        return result.scalars().all()
    except SQLAlchemyError:
        raise


# UPDATE
async def update_partner(db: AsyncSession, partner_id: int, partner_in: PartnerUpdate) -> Optional[Partner]:
    try:
        result = await db.execute(select(Partner).where(Partner.id == partner_id))
        db_partner = result.scalars().first()

        if not db_partner:
            return None

        update_data = partner_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_partner, field, value)

        await db.commit()
        await db.refresh(db_partner)
        return db_partner
    except IntegrityError:
        await db.rollback()
        raise
    except SQLAlchemyError:
        await db.rollback()
        raise


# DELETE
async def delete_partner(db: AsyncSession, partner_id: int) -> bool:
    try:
        result = await db.execute(delete(Partner).where(Partner.id == partner_id))  # Эффективное удаление
        await db.commit()
        return result.rowcount > 0
    except SQLAlchemyError:
        await db.rollback()
        raise