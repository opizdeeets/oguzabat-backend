# app/services/vacancy_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, UploadFile
from typing import Optional, List

from app.models.models import Vacancy, Company
from app.schemas.schemas import VacancyCreate, VacancyUpdate
from app.core.uploads import save_uploaded_file, delete_uploaded_file


# --------------------- CREATE ---------------------
async def create_vacancy(
    db: AsyncSession,
    vacancy_in: VacancyCreate,
    company_id: int,
    logo: Optional[UploadFile] = None,
    max_mb: int = 2
) -> Vacancy:
    try:
        vacancy_data = vacancy_in.model_dump()
        vacancy_data["company_id"] = company_id

        if logo:
            logo_path = await save_uploaded_file(logo, sub_dir="logos", max_mb=max_mb)
            vacancy_data["logo_path"] = logo_path

        db_vacancy = Vacancy(**vacancy_data)
        db.add(db_vacancy)
        await db.commit()
        await db.refresh(db_vacancy)
        return db_vacancy

    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Ошибка целостности данных: {e.orig}")
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при создании вакансии: {e}")


# --------------------- READ ONE ---------------------
async def get_vacancy(db: AsyncSession, vacancy_id: int) -> Optional[Vacancy]:
    try:
        result = await db.execute(
            select(Vacancy)
            .options(selectinload(Vacancy.company))  # подгружаем компанию
            .where(Vacancy.id == vacancy_id)
        )
        return result.scalars().first()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении вакансии: {e}")


# --------------------- READ ALL ---------------------
async def get_vacancies(db: AsyncSession) -> List[Vacancy]:
    try:
        result = await db.execute(
            select(Vacancy).options(selectinload(Vacancy.company))  # подгружаем компанию
        )
        return result.scalars().all()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении списка вакансий: {e}")


# --------------------- UPDATE ---------------------
async def update_vacancy(
    db: AsyncSession,
    vacancy_id: int,
    vacancy_in: VacancyUpdate,
    logo: Optional[UploadFile] = None,
    max_mb: int = 2,
    company_id: Optional[int] = None
) -> Optional[Vacancy]:
    try:
        result = await db.execute(
            select(Vacancy).options(selectinload(Vacancy.company)).where(Vacancy.id == vacancy_id)
        )
        db_vacancy = result.scalars().first()

        if not db_vacancy:
            raise HTTPException(status_code=404, detail=f"Vacancy with id={vacancy_id} not found")

        update_data = vacancy_in.model_dump(exclude_unset=True)
        if company_id:
            update_data["company_id"] = company_id

        for field, value in update_data.items():
            setattr(db_vacancy, field, value)

        if logo:
            if getattr(db_vacancy, "logo_path", None):
                await delete_uploaded_file(db_vacancy.logo_path)
            logo_path = await save_uploaded_file(logo, sub_dir="logos", max_mb=max_mb)
            db_vacancy.logo_path = logo_path

        await db.commit()
        await db.refresh(db_vacancy)
        return db_vacancy

    except HTTPException:
        raise
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Ошибка целостности данных: {e.orig}")
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при обновлении вакансии: {e}")


# --------------------- DELETE ---------------------
async def delete_vacancy(db: AsyncSession, vacancy_id: int) -> bool:
    try:
        result = await db.execute(
            select(Vacancy).options(selectinload(Vacancy.company)).where(Vacancy.id == vacancy_id)
        )
        vacancy = result.scalars().first()

        if not vacancy:
            raise HTTPException(status_code=404, detail=f"Vacancy with id={vacancy_id} not found")

        if getattr(vacancy, "logo_path", None):
            await delete_uploaded_file(vacancy.logo_path)

        await db.delete(vacancy)
        await db.commit()
        return True

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при удалении вакансии: {e}")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Непредвиденная ошибка при удалении вакансии: {e}")


# --------------------- CRUD COMPANY ---------------------
async def get_company(db: AsyncSession, company_id: int) -> Optional[Company]:
    try:
        result = await db.execute(
            select(Company)
            .options(selectinload(Company.vacancies))  # подгружаем все вакансии компании
            .where(Company.id == company_id)
        )
        return result.scalars().first()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении компании: {e}")


async def get_companies(db: AsyncSession) -> List[Company]:
    try:
        result = await db.execute(
            select(Company).options(selectinload(Company.vacancies))  # подгружаем вакансии
        )
        return result.scalars().all()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении списка компаний: {e}")
