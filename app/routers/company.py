from fastapi import APIRouter, Depends, UploadFile, Form, Path, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.db import get_db
from app.core.deps import get_current_user, get_current_admin_user
from app.schemas.schemas import CompanyCreate, CompanyUpdate, CompanyRead, Message
from app.services import company_service as crud_company
from app.core.uploads import save_uploaded_file, update_entity  # универсальный аплоудер

router = APIRouter(prefix="/companies", tags=["companies"])

# ---------------- CREATE ----------------
@router.post("/", response_model=CompanyRead, status_code=status.HTTP_201_CREATED)
async def create_company(
    name: str = Form(..., description="Название компании"),
    description: str = Form(..., description="Описание компании"),
    website: str = Form(..., description="Сайт компании"),
    categories: Optional[str] = Form("", description="Категории через запятую"),
    logo: Optional[UploadFile] = None,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),  # JWT только здесь
):
    categories_list = [c.strip() for c in categories.split(",") if c.strip()]
    logo_path = None
    if logo:
        logo_path = await save_uploaded_file(logo, sub_dir="logos")

    company_in = CompanyCreate(
        name=name,
        description=description,
        website=website,
        categories=categories_list,
        logo_path=logo_path or "",
    )
    try:
        return await crud_company.create_company(db, company_in)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка создания компании: {e}")


# ---------------- UPDATE COMPANY ----------------
@router.put("/{company_id}", response_model=CompanyRead)
async def update_company(
    company_id: int = Path(..., gt=0),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    website: Optional[str] = Form(None),
    logo: Optional[UploadFile] = None,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    company_in = CompanyUpdate(
        name=name,
        description=description,
        website=website
    )
    return await update_entity(
        db=db,
        entity_id=company_id,
        entity_in=company_in,
        crud_update_func=crud_company.update_company,
        file=logo,
        file_sub_dir="company_logos"
    )


# ---------------- GET LIST ----------------
@router.get("/", response_model=List[CompanyRead])
async def list_companies(db: AsyncSession = Depends(get_db)):
    try:
        return await crud_company.get_companies(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения списка компаний: {e}")


# ---------------- GET SINGLE ----------------
@router.get("/{company_id}", response_model=CompanyRead)
async def get_company(company_id: int = Path(..., gt=0), db: AsyncSession = Depends(get_db)):
    company = await crud_company.get_company(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


# ---------------- DELETE ----------------
@router.delete("/{company_id}", response_model=Message)
async def delete_company(
    company_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),  # JWT только здесь
):
    deleted = await crud_company.delete_company(db, company_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Company not found")
    return {"success": True, "message": "Company deleted successfully."}
