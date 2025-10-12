from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.sql import update
from fastapi import UploadFile, HTTPException, status
from typing import List, Optional

from app.models.models import Company
from app.schemas.schemas import CompanyCreate, CompanyUpdate
from app.core.uploads import save_uploaded_file, delete_uploaded_file, update_entity


async def _update_company_dict(
    db: AsyncSession,
    entity_id: int,
    data: dict
):
    """
    Обновляет компанию по ID, используя переданные поля.
    Возвращает обновлённый объект Company.
    """
    query = (
        update(Company)
        .where(Company.id == entity_id)
        .values(**data)
        .returning(Company)
    )
    result = await db.execute(query)
    updated_company = result.scalar_one_or_none()

    if not updated_company:
        return None

    await db.commit()
    await db.refresh(updated_company)
    return updated_company


# ---------------- CREATE ----------------
async def create_company(
    db: AsyncSession,
    company_in: CompanyCreate,
    logo_file: Optional[UploadFile] = None
) -> Company:
    """
    Создаёт компанию с поддержкой загрузки логотипа.
    Даты (created_at, updated_at) назначаются на уровне БД автоматически.
    """
    try:
        logo_path = None
        if logo_file:
            logo_path = await save_uploaded_file(logo_file, "logos")

        company_data = company_in.dict(exclude_none=True)

        if logo_path is not None:
            company_data["logo_path"] = logo_path

        if "categories" not in company_data:
            company_data["categories"] = []

        db_company = Company(**company_data)
        db.add(db_company)
        await db.commit()
        await db.refresh(db_company)
        return db_company

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Компания с таким именем или email уже существует."
        )
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- READ ONE ----------------
async def get_company(db: AsyncSession, company_id: int) -> Optional[Company]:
    """
    Возвращает компанию по ID с проектами и вакансиями.
    """
    try:
        result = await db.execute(
            select(Company)
            .options(
                selectinload(Company.projects),
                selectinload(Company.vacancies)  # добавляем вакансии
            )
            .where(Company.id == company_id)
        )
        return result.scalars().first()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- READ ALL ----------------
async def get_companies(
    db: AsyncSession,
    categories: Optional[List[str]] = None
) -> List[Company]:
    """
    Возвращает все компании, фильтруя по категориям (если заданы).
    """
    try:
        stmt = select(Company).options(
            selectinload(Company.projects),
            selectinload(Company.vacancies)  # добавляем вакансии
        )

        if categories:
            stmt = stmt.where(Company.categories.overlap(categories))

        stmt = stmt.order_by(Company.created_at.desc())
        result = await db.execute(stmt)
        return result.scalars().all()

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- UPDATE ----------------
async def update_company(
    db: AsyncSession,
    company_id: int,
    company_in: CompanyUpdate,
    logo_file: Optional[UploadFile] = None
) -> Optional[Company]:
    """
    Обновляет компанию и логотип.
    updated_at обновится автоматически за счёт onupdate=func.now().
    """
    return await update_entity(
        db=db,
        entity_id=company_id,
        entity_in=company_in,
        crud_update_func=_update_company_dict,
        model_class=Company,  # обязательно
        file=logo_file,
        sub_dir="company_logos"
    )


# ---------------- DELETE ----------------
async def delete_company(db: AsyncSession, company_id: int) -> bool:
    """
    Удаляет компанию и связанные ресурсы (логотип, проекты, вакансии).
    """
    try:
        result = await db.execute(select(Company).where(Company.id == company_id))
        db_company = result.scalars().first()
        if not db_company:
            return False

        # Удаляем логотип, если есть
        if db_company.logo_path:
            await delete_uploaded_file(db_company.logo_path)

        await db.delete(db_company)
        await db.commit()
        return True

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
