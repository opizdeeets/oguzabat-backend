from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import List, Optional

from app.core.db import get_db
from app.core.deps import get_current_admin_user
from app.models.models import ContactForm
from app.schemas.schemas import ContactFormCreate, ContactFormUpdate, ContactFormRead, Message
from app.services import contact_form_service as contact_crud

router = APIRouter(prefix="/contact", tags=["contact"])

@router.post("/", response_model=ContactFormRead, status_code=status.HTTP_201_CREATED)
async def create_contact_form(
    contact_in: ContactFormCreate = Body(..., description="Contact form data"),
    db: AsyncSession = Depends(get_db)
):
    try:
        created = await contact_crud.create_contact_form(db, contact_in)
        return created
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Could not create contact form. Possibly duplicate or invalid fields.")
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

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
    except Exception:
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
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{contact_id}", response_model=ContactFormRead)
async def update_contact_form(
    contact_id: int = Path(..., gt=0, example=1, description="Contact Form ID"),
    contact_in: ContactFormUpdate = Body(..., description="Contact form data to update"),
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(get_current_admin_user)
):
    try:
        updated = await contact_crud.update_contact_form(db, contact_id, contact_in.dict(exclude_unset=True))
        if not updated:
            raise HTTPException(status_code=404, detail="Contact form not found")
        return updated
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Could not update contact form. Possibly duplicate or invalid fields.")
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{contact_id}", response_model=Message)
async def delete_contact_form(
    contact_id: int = Path(..., gt=0, example=1, description="Contact Form ID"),
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(get_current_admin_user)
):
    try:
        deleted = await contact_crud.delete_contact_form(db, contact_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Contact form not found")
        return {"success": True, "message": "Contact form deleted successfully"}
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Could not delete contact form. Possibly dependent records exist.")
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")