from fastapi import (
    APIRouter, Depends, UploadFile, Form, Path, status, HTTPException, File
)
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.db import get_db
from app.core.deps import get_current_user
from app.schemas.schemas import CompanyCreate, CompanyUpdate, CompanyRead
from app.models.models import Company
from app.services import company_service as crud_company
from app.core.uploads import save_uploaded_file, update_entity  # универсальный аплоудер


router = APIRouter(prefix="/companies", tags=["Companies"])


# ---------------- CREATE ----------------
@router.post("/", response_model=CompanyRead, status_code=status.HTTP_201_CREATED)
async def create_company(
    name: str = Form(..., description="Название компании"),
    description: str = Form(..., description="Описание компании"),
    email: str = Form(..., description="email of company"),
    website: str = Form(..., description="Сайт компании"),
    categories: Optional[str] = Form("", description="Категории через запятую"),
    logo: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),  # JWT только здесь
):
    """
    Создаёт новую компанию. Поля created_at и updated_at выставляются автоматически.
    """
    categories_list = [c.strip() for c in categories.split(",") if c.strip()]

    logo_path = None
    if logo:
        logo_path = await save_uploaded_file(logo, sub_dir="logos")

    company_in = CompanyCreate(
        name=name,
        description=description,
        website=website,
        email=email,
        categories=categories_list,
        logo_path=logo_path
    )

    try:
        return await crud_company.create_company(db, company_in)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка создания компании: {e}")


# ---------------- UPDATE ----------------
@router.put("/{company_id}", response_model=CompanyRead)
async def update_company(
    company_id: int = Path(..., gt=0),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    website: Optional[str] = Form(None),
    logo: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """
    Обновляет данные компании. Если передан новый логотип — заменяет старый файл.
    """
    company_in = CompanyUpdate(
        name=name,
        description=description,
        website=website,
    )

    return await update_entity(
        db=db,
        entity_id=company_id,
        entity_in=company_in,
        crud_update_func=crud_company.update_company,
        model_class=Company,
        file=logo,
        sub_dir="company_logos",
        file_field="logo_path"
    )


# ---------------- READ LIST ----------------
@router.get("/", response_model=List[CompanyRead])
async def list_companies(db: AsyncSession = Depends(get_db)):
    """
    Возвращает список всех компаний.
    """
    try:
        return await crud_company.get_companies(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения списка компаний: {e}")


# ---------------- READ SINGLE ----------------
@router.get("/{company_id}", response_model=CompanyRead)
async def get_company(
    company_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
):
    """
    Возвращает информацию о компании по ID.
    """
    company = await crud_company.get_company(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


# ---------------- DELETE ----------------
@router.delete("/{company_id}", response_model=bool)
async def delete_company(
    company_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    deleted = await crud_company.delete_company(db, company_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Company not found")
    return True
