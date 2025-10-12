from fastapi import APIRouter, Depends, HTTPException, status, Path, Body, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import List, Optional

from app.core.db import get_db
from app.core.deps import get_current_admin_user
from app.models.models import ContactForm
from app.schemas.schemas import ContactFormCreate, ContactFormUpdate, ContactFormRead
from app.services import contact_form_service as contact_crud

router = APIRouter(prefix="/contact", tags=["contact"])

@router.post("/", response_model=ContactFormRead, status_code=status.HTTP_201_CREATED)
async def create_contact_form(
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    phone_number: str = Form(...),
    company_name: str = Form(...),
    message: str = Form(...),
    map_code: str | None = Form(default="", description="HTML/JS код карты (необязательное поле)"),
    db: AsyncSession = Depends(get_db)
):
    # Конвертируем пустую строку в None
    if map_code == "":
        map_code = None

    contact_in = ContactFormCreate(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone_number=phone_number,
        company_name=company_name,
        message=message
    )

    created = await contact_crud.create_contact_form(db, contact_in)

    if map_code is not None:
        created.map_code = map_code
        db.add(created)
        await db.commit()
        await db.refresh(created)

    return created

@router.get("/", response_model=List[ContactFormRead])
async def get_contact_forms(
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(get_current_admin_user)
):
    try:
        items = await contact_crud.get_contact_forms(db)
        return items
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{contact_id}", response_model=ContactFormRead)
async def get_contact_form(
    contact_id: int = Path(..., gt=0, example=1, description="Contact Form ID"),
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(get_current_admin_user)
):
    try:
        contact = await contact_crud.get_contact_form(db, contact_id)
        if not contact:
            raise HTTPException(status_code=404, detail="Contact form not found")
        return contact
    except HTTPException:
        # Пробрасываем точные HTTPException (например 404) дальше
        raise
    except SQLAlchemyError as e:
        # Конкретная ошибка БД
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        # Любые другие неожиданные ошибки
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

@router.put("/{contact_id}", response_model=ContactFormRead)
async def update_contact_form(
    contact_id: int = Path(..., gt=0, example=1, description="Contact Form ID"),
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    phone_number: str = Form(...),
    company_name: str = Form(...),
    message: str = Form(...),
    map_code: str | None = Form(default=None, description="HTML/JS код карты (необязательное поле)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing contact form entry.
    Accepts data via form fields instead of raw JSON.
    """
    try:
        contact_in = ContactFormUpdate(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            company_name=company_name,
            message=message
        )

        updated = await contact_crud.update_contact_form(
            db=db,
            contact_form_id=contact_id,
            contact_form_in=contact_in,
            map_code=map_code
        )

        if not updated:
            raise HTTPException(status_code=404, detail="Contact form not found")

        return updated

    except IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="Could not update contact form. Possibly duplicate or invalid fields."
        )
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")



@router.delete("/{contact_id}", response_model=bool)
async def delete_contact_form(
    contact_id: int = Path(..., gt=0, example=1, description="Contact Form ID"),
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(get_current_admin_user)
):
    try:
        deleted = await contact_crud.delete_contact_form(db, contact_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Contact form not found")
        return True
    except HTTPException:
        # Пробрасываем точные HTTPException (например 404) дальше
        raise
    except SQLAlchemyError as e:
        # Конкретная ошибка БД
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        # Любые другие неожиданные ошибки
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")