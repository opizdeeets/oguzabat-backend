from fastapi import APIRouter, Depends, UploadFile, Form, Path, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.db import get_db
from app.core.deps import get_current_user  # JWT авторизация
from app.schemas.schemas import PartnerCreate, PartnerUpdate, PartnerRead, Message
from app.services import partner_service as partner_crud
from app.core.uploads import save_uploaded_file, update_entity  # универсальный аплоудер

router = APIRouter(prefix="/partners", tags=["partners"])

# ---------------- CREATE ----------------
@router.post("/", response_model=PartnerRead, status_code=status.HTTP_201_CREATED)
async def create_partner(
    name: str = Form(..., description="Название партнёра"),
    description: str = Form(..., description="Описание партнёра"),
    website: str = Form(..., description="Сайт партнёра"),
    logo: Optional[UploadFile] = None,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),  # JWT только здесь
):
    logo_path = None
    if logo:
        logo_path = await save_uploaded_file(logo, sub_dir="partners", max_size_mb=2)

    partner_in = PartnerCreate(
        name=name,
        description=description,
        website=website,
        logo_path=logo_path or "",
    )
    try:
        return await partner_crud.create_partner(db, partner_in)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка создания партнёра: {e}")


# ---------------- UPDATE ----------------
@router.put("/{partner_id}", response_model=PartnerRead)
async def update_partner(
    partner_id: int = Path(..., gt=0),
    partner_in: PartnerUpdate = Form(...),
    logo: Optional[UploadFile] = None,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),  # JWT только здесь
):
    return await update_entity(
        db=db,
        entity_id=partner_id,
        entity_in=partner_in,
        crud_update_func=partner_crud.update_partner,
        file=logo,
        file_sub_dir="partners",
    )


# ---------------- GET LIST ----------------
@router.get("/", response_model=List[PartnerRead])
async def list_partners(db: AsyncSession = Depends(get_db)):
    try:
        return await partner_crud.get_partners(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения списка партнёров: {e}")


# ---------------- GET SINGLE ----------------
@router.get("/{partner_id}", response_model=PartnerRead)
async def get_partner(partner_id: int = Path(..., gt=0), db: AsyncSession = Depends(get_db)):
    partner = await partner_crud.get_partner(db, partner_id)
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    return partner


# ---------------- DELETE ----------------
@router.delete("/{partner_id}", response_model=Message)
async def delete_partner(
    partner_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),  # JWT только здесь
):
    deleted = await partner_crud.delete_partner(db, partner_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Partner not found")
    return {"success": True, "message": "Partner deleted successfully"}
