from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import List, Optional

from app.core.db import get_db
from app.core.deps import get_current_admin_user
from app.models.models import Vacancy
from app.schemas.schemas import VacancyCreate, VacancyUpdate, VacancyRead, Message
from app.services import vacancy_service as vacancy_crud

router = APIRouter(prefix="/vacancies", tags=["vacancies"])

@router.post("/", response_model=VacancyRead, status_code=status.HTTP_201_CREATED)
async def create_vacancy(
    vacancy_in: VacancyCreate = Body(..., description="Vacancy data to create"),
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(get_current_admin_user)
):
    try:
        created = await vacancy_crud.create_vacancy(db, vacancy_in)
        return created
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Could not create vacancy. Possibly duplicate or invalid fields.")
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=List[VacancyRead])
async def get_vacancies(
    db: AsyncSession = Depends(get_db)
):
    try:
        items = await vacancy_crud.get_vacancies(db)
        return items
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{vacancy_id}", response_model=VacancyRead)
async def get_vacancy(
    vacancy_id: int = Path(..., gt=0, example=1, description="Vacancy ID"),
    db: AsyncSession = Depends(get_db)
):
    try:
        vacancy = await vacancy_crud.get_vacancy(db, vacancy_id)
        if not vacancy:
            raise HTTPException(status_code=404, detail="Vacancy not found")
        return vacancy
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{vacancy_id}", response_model=VacancyRead)
async def update_vacancy(
    vacancy_id: int = Path(..., gt=0, example=1, description="Vacancy ID"),
    vacancy_in: VacancyUpdate = Body(..., description="Vacancy data to update"),
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(get_current_admin_user)
):
    try:
        updated = await vacancy_crud.update_vacancy(db, vacancy_id, vacancy_in.dict(exclude_unset=True))
        if not updated:
            raise HTTPException(status_code=404, detail="Vacancy not found")
        return updated
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Could not update vacancy. Possibly duplicate or invalid fields.")
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{vacancy_id}", response_model=Message)
async def delete_vacancy(
    vacancy_id: int = Path(..., gt=0, example=1, description="Vacancy ID"),
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(get_current_admin_user)
):
    try:
        deleted = await vacancy_crud.delete_vacancy(db, vacancy_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Vacancy not found")
        return {"success": True, "message": "Vacancy deleted successfully"}
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Could not delete vacancy. Possibly dependent records exist.")
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")