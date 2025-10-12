from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Form,
    File,
    UploadFile,
    Path
)
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.core.db import get_db
from app.schemas.schemas import VacancyCreate, VacancyRead, VacancyUpdate
from app.services.vacancy_service import (
    create_vacancy,
    get_vacancy,
    get_vacancies,
    update_vacancy,
    delete_vacancy,
)
from app.core.deps import get_current_admin_user  # если требуется
from app.core.deps import get_current_user
from app.schemas.schemas import EmploymentType

router = APIRouter(prefix="/vacancies", tags=["Vacancies"])


# --------------------- CREATE ---------------------
@router.post(
    "/",
    response_model=VacancyRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новую вакансию",
    description="Создает вакансию с опциональным логотипом. Доступно только администратору."
)
async def create_vacancy_endpoint(
    title: str = Form(..., description="Название вакансии"),
    description: str = Form(..., description="Описание вакансии"),
    location: Optional[str] = Form(None, description="Местоположение"),
    employment_type: Optional[EmploymentType] = Form(None, description="Тип занятости"),
    company_id: int = Form(..., description="ID компании, к которой относится вакансия"),  # добавлено
    logo: Optional[UploadFile] = File(None, description="Логотип компании (до 2МБ по умолчанию)"),
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin_user)
):
    try:
        vacancy_in = VacancyCreate(
            title=title,
            description=description,
            location=location,
            employment_type=employment_type,
        )
        vacancy = await create_vacancy(db, vacancy_in, company_id=company_id, logo=logo)
        return vacancy
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при создании вакансии: {e}")



# --------------------- READ ALL ---------------------
@router.get(
    "/",
    response_model=List[VacancyRead],
    summary="Получить список всех вакансий",
    description="Возвращает все вакансии без пагинации и фильтрации."
)
async def get_all_vacancies(
    db: AsyncSession = Depends(get_db)
):
    try:
        vacancies = await get_vacancies(db)
        return vacancies
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении списка вакансий: {e}")


# --------------------- READ ONE ---------------------
@router.get(
    "/{vacancy_id}",
    response_model=VacancyRead,
    summary="Получить вакансию по ID",
    description="Возвращает одну вакансию по её идентификатору."
)
async def get_vacancy_by_id(
    vacancy_id: int = Path(..., gt=0, description="ID вакансии"),
    db: AsyncSession = Depends(get_db)
):
    vacancy = await get_vacancy(db, vacancy_id)
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    return vacancy


# --------------------- UPDATE ---------------------
@router.put(
    "/{vacancy_id}",
    response_model=VacancyRead,
    summary="Обновить вакансию",
    description="Обновляет вакансию и заменяет логотип при необходимости. Доступно только администратору."
)
async def update_vacancy_endpoint(
    vacancy_id: int = Path(..., gt=0, description="ID вакансии"),
    title: Optional[str] = Form(None, description="Название вакансии"),
    description: Optional[str] = Form(None, description="Описание вакансии"),
    location: Optional[str] = Form(None, description="Местоположение"),
    employment_type: Optional[EmploymentType] = Form(None, description="Тип занятости"),
    company_id: Optional[int] = Form(None, description="ID компании, к которой относится вакансия"),  # добавлено
    logo: Optional[UploadFile] = File(None, description="Новый логотип компании"),
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin_user)
):
    vacancy_in = VacancyUpdate(
        title=title,
        description=description,
        location=location,
        employment_type=employment_type,
    )

    try:
        updated = await update_vacancy(db, vacancy_id, vacancy_in, logo=logo, company_id=company_id)
        return updated
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обновлении вакансии: {e}")



# --------------------- DELETE ---------------------
@router.delete(
    "/{vacancy_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить вакансию",
    description="Удаляет вакансию по ID и удаляет её логотип, если он есть. Доступно только администратору."
)
async def delete_vacancy_endpoint(
    vacancy_id: int = Path(..., gt=0, description="ID вакансии"),
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin_user)
):
    try:
        deleted = await delete_vacancy(db, vacancy_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Vacancy not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при удалении вакансии: {e}")
