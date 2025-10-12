# app/api/v1/application_router.py

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, Form, Path, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.schemas.schemas import ApplicationCreate, ApplicationUpdate, ApplicationRead
from app.services import application_service as application_crud
from app.core.db import get_db
from app.core.deps import get_current_admin_user

router = APIRouter(prefix="/applications", tags=["Applications"])


# ---------------- CREATE ----------------
@router.post("/", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
async def create_application(
    vacancy_id: int = Form(...),
    name: str = Form(...),
    surname: str = Form(...),
    email: str = Form(...),
    phone_number: str = Form(...),
    message: Optional[str] = Form(None),
    portfolio_files: Optional[List[UploadFile]] = File(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Создать отклик на вакансию. Дата создаётся автоматически в БД.
    """
    application_in = ApplicationCreate(
        vacancy_id=vacancy_id,
        name=name,
        surname=surname,
        email=email,
        phone_number=phone_number,
        message=message,
    )
    try:
        created = await application_crud.create_application(
            db=db,
            application_in=application_in,
            files=portfolio_files,
        )
        return created
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Invalid or duplicate application data.")
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


# ---------------- READ ALL ----------------
@router.get("/", response_model=List[ApplicationRead])
async def list_applications(
    vacancy_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(get_current_admin_user),
):
    """
    Получить список откликов (опционально отфильтрованных по вакансии).
    """
    return await application_crud.get_applications(db, vacancy_id)


# ---------------- READ ONE ----------------
@router.get("/{application_id}", response_model=ApplicationRead)
async def get_application(
    application_id: int = Path(..., gt=0, description="ID отклика"),
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(get_current_admin_user),
):
    """
    Получить отклик по ID.
    """
    app_obj = await application_crud.get_application(db, application_id)
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")
    return app_obj


# ---------------- UPDATE ----------------
@router.put("/{application_id}", response_model=ApplicationRead)
async def update_application(
    application_id: int = Path(..., gt=0, description="ID отклика"),
    name: Optional[str] = Form(None),
    surname: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone_number: Optional[str] = Form(None),
    message: Optional[str] = Form(None),
    portfolio_files: Optional[List[UploadFile]] = File(None),
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(get_current_admin_user),
):
    """
    Обновить отклик и, при необходимости, добавить новые файлы.
    """
    update_data = {
        "name": name,
        "surname": surname,
        "email": email,
        "phone_number": phone_number,
        "message": message,
    }

    updated = await application_crud.update_application(
        db=db,
        application_id=application_id,
        update_data=update_data,
        new_files=portfolio_files,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Application not found")
    return updated


# ---------------- DELETE ----------------
@router.delete("/{application_id}", response_model=bool)
async def delete_application(
    application_id: int = Path(..., gt=0, description="ID отклика"),
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(get_current_admin_user),
):
    """
    Удалить отклик и связанные файлы.
    """
    deleted = await application_crud.delete_application(db, application_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Application not found")
    return True
