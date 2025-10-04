from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.models.models import Vacancy
from app.schemas.schemas import VacancyCreate, VacancyUpdate
from typing import List, Optional

# CREATE
async def create_vacancy(db: AsyncSession, vacancy_in: VacancyCreate) -> Vacancy:
    try:
        db_vacancy = Vacancy(**vacancy_in.dict())
        db.add(db_vacancy)
        await db.commit()
        await db.refresh(db_vacancy)
        return db_vacancy
    except IntegrityError:
        await db.rollback()
        raise
    except SQLAlchemyError:
        await db.rollback()
        raise

# READ one
async def get_vacancy(db: AsyncSession, vacancy_id: int) -> Optional[Vacancy]:
    try:
        result = await db.execute(select(Vacancy).where(Vacancy.id == vacancy_id))
        return result.scalars().first()
    except SQLAlchemyError:
        raise

# READ all
async def get_vacancies(db: AsyncSession) -> List[Vacancy]:
    try:
        result = await db.execute(select(Vacancy))
        return result.scalars().all()
    except SQLAlchemyError:
        raise

# UPDATE
async def update_vacancy(db: AsyncSession, vacancy_id: int, vacancy_in: VacancyUpdate) -> Optional[Vacancy]:
    try:
        result = await db.execute(select(Vacancy).where(Vacancy.id == vacancy_id))
        db_vacancy = result.scalars().first()

        if not db_vacancy:
            return None

        update_data = vacancy_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_vacancy, field, value)

        await db.commit()
        await db.refresh(db_vacancy)
        return db_vacancy
    except IntegrityError:
        await db.rollback()
        raise
    except SQLAlchemyError:
        await db.rollback()
        raise

# DELETE
async def delete_vacancy(db: AsyncSession, vacancy_id: int) -> bool:
    try:
        result = await db.execute(delete(Vacancy).where(Vacancy.id == vacancy_id))
        await db.commit()
        return result.rowcount > 0
    except SQLAlchemyError:
        await db.rollback()
        raise