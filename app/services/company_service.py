from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import UploadFile, HTTPException, status
from typing import List, Optional

from app.models.models import Company
from app.schemas.schemas import CompanyCreate, CompanyUpdate
from app.core.uploads import save_uploaded_file, delete_uploaded_file, update_entity


# ---------------- CREATE ----------------
async def create_company(
    db: AsyncSession,
    company_in: CompanyCreate,
    logo_file: Optional[UploadFile] = None
) -> Company:
    """
    Создаёт компанию с поддержкой загрузки логотипа.
    """
    try:
        # Сохраняем логотип, если есть
        logo_path = None
        if logo_file:
            logo_path = await save_uploaded_file(logo_file, "logos")
            print("DEBUG: logo_path =", logo_path)
        else:
            print("DEBUG: logo_file not provided")
        company_data_dict = company_in.dict(exclude={"logo_path"})
        db_company = Company(**company_data_dict, logo_path=logo_path)
        db.add(db_company)
        await db.commit()
        await db.refresh(db_company)
        return db_company

    except IntegrityError:
        await db.rollback()
        raise
    except SQLAlchemyError:
        await db.rollback()
        raise


# ---------------- READ ONE ----------------
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


# ---------------- READ ALL ----------------
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


# ---------------- UPDATE ----------------
async def update_company(
    db: AsyncSession,
    company_id: int,
    company_in: CompanyUpdate,
    logo_file: Optional[UploadFile] = None
) -> Optional[Company]:
    """
    Обновляет компанию и логотип.
    """
    return await update_entity(
        db=db,
        entity_id=company_id,
        entity_in=company_in,
        crud_update_func=_update_company_dict,
        file=logo_file,
        file_sub_dir="logo"
    )


# Вспомогательная функция для update_entity
async def _update_company_dict(db: AsyncSession, company_id: int, update_data: dict) -> Optional[Company]:
    result = await db.execute(select(Company).where(Company.id == company_id))
    db_company = result.scalars().first()
    if not db_company:
        return None

    for field, value in update_data.items():
        setattr(db_company, field, value)

    await db.commit()
    await db.refresh(db_company)
    return db_company


# ---------------- DELETE ----------------
async def delete_company(db: AsyncSession, company_id: int) -> bool:
    """
    Удаляет компанию и все связанные файлы (логотип, портфолио).
    """
    result = await db.execute(select(Company).where(Company.id == company_id))
    db_company = result.scalars().first()
    if not db_company:
        return False

    # Удаляем логотип
    if db_company.logo_path:
        await delete_uploaded_file(db_company.logo_path)

    # TODO: Если есть портфолио (массив файлов) — удалить все через delete_uploaded_file

    await db.delete(db_company)
    await db.commit()
    return True
