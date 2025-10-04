from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.models.models import Company
from app.schemas.schemas import CompanyCreate, CompanyUpdate
from typing import List, Optional


# CREATE
async def create_company(db: AsyncSession, company_in: CompanyCreate) -> Company:
    try:
        db_company = Company(**company_in.dict())
        db.add(db_company)
        await db.commit()
        await db.refresh(db_company)
        return db_company
    except IntegrityError:
        await db.rollback()
        raise
    except SQLAlchemyError as e:
        await db.rollback()
        raise


# READ one
async def get_company(db: AsyncSession, company_id: int) -> Optional[Company]:
    try:
        result = await db.execute(
            select(Company)
            .options(selectinload(Company.projects))
            .where(Company.id == company_id)
        )
        return result.scalars().first()
    except SQLAlchemyError:
        raise


# READ all (БЕЗ пагинации)
async def get_companies(db: AsyncSession, categories: Optional[List[str]] = None) -> List[Company]:
    try:
        stmt = select(Company).options(selectinload(Company.projects))

        if categories: 
            stmt = stmt.where(Company.categories.overlap(categories))

        stmt = stmt.order_by(Company.created_at.desc())
        result = await db.execute(stmt)
        return result.scalars().all()
    except SQLAlchemyError:
        raise


# UPDATE
async def update_company(db: AsyncSession, company_id: int, company_in: CompanyUpdate) -> Optional[Company]:
    try:
        result = await db.execute(select(Company).where(Company.id == company_id))  # Убрал selectinload
        db_company = result.scalars().first()

        if not db_company:
            return None

        update_data = company_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_company, field, value)

        await db.commit()
        await db.refresh(db_company)
        return db_company
    except IntegrityError:
        await db.rollback()
        raise
    except SQLAlchemyError:
        await db.rollback()
        raise


# DELETE
async def delete_company(db: AsyncSession, company_id: int) -> bool:
    try:
        result = await db.execute(delete(Company).where(Company.id == company_id))  # Эффективное удаление
        await db.commit()
        return result.rowcount > 0
    except SQLAlchemyError:
        await db.rollback()
        raise