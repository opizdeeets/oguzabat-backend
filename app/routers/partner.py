from fastapi import APIRouter, Depends, UploadFile, Form, Path, status, HTTPException, File
from pyasn1.type.univ import Boolean
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.db import get_db
from app.core.deps import get_current_user  # JWT авторизация
from app.models.models import Partner
from app.schemas.schemas import PartnerCreate, PartnerUpdate, PartnerRead
from app.services import partner_service as partner_crud
from app.core.uploads import save_uploaded_file, update_entity  # универсальный аплоудер

router = APIRouter(prefix="/partners", tags=["partners"])

# ---------------- CREATE ----------------
@router.post("/", response_model=PartnerRead, status_code=status.HTTP_201_CREATED)
async def create_partner(
    name: str = Form(...),
    slogan: str = Form(...),
    short_description: str = Form(...),
    email: str = Form(...),
    logo: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db)
):
    partner_in = PartnerCreate(
        name=name,
        slogan=slogan,
        short_description=short_description,
        email=email,
        logo_path=""  # пока пусто, логотип обрабатываем в сервисе
    )

    try:
        return await partner_crud.create_partner(db, partner_in, logo_file=logo)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка создания партнёра: {e}")


# ---------------- UPDATE ----------------
@router.put("/{partner_id}", response_model=PartnerRead)
async def update_partner(
    partner_id: int = Path(..., gt=0),
    name: Optional[str] = Form(None),
    slogan: Optional[str] = Form(None),
    short_description: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    logo: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Обновление партнёра с формами и возможностью загрузки нового логотипа.
    """
    # Формируем словарь для update_entity
    update_data = {}
    if name is not None:
        update_data["name"] = name
    if slogan is not None:
        update_data["slogan"] = slogan
    if short_description is not None:
        update_data["short_description"] = short_description
    if email is not None:
        update_data["email"] = email

    # Если нет данных и нет файла — ошибка
    if not update_data and not logo:
        raise HTTPException(
            status_code=400, detail="Нет данных для обновления"
        )

    return await update_entity(
        db=db,
        entity_id=partner_id,
        entity_in=update_data,
        crud_update_func=partner_crud.update_partner,
        file=logo,
        sub_dir="partners",
        model_class=Partner,
        file_field="logo_path",  # явно указываем поле для файла
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
@router.delete("/{partner_id}", response_model=bool)
async def delete_partner(
    partner_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),  # JWT только здесь
):
    deleted = await partner_crud.delete_partner(db, partner_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Partner not found")
    return True
