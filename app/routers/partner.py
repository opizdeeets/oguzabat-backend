from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import List, Optional

from app.core.db import get_db
from app.core.deps import get_current_admin_user
from app.models.models import Partner
from app.schemas.schemas import PartnerCreate, PartnerUpdate, PartnerRead, Message
from app.services import partner_service as partner_crud

router = APIRouter(prefix="/partners", tags=["partners"])

@router.post("/", response_model=PartnerRead, status_code=status.HTTP_201_CREATED)
async def create_partner(
    partner_in: PartnerCreate = Body(..., description="Partner data to create"),
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(get_current_admin_user)
):
    try:
        created = await partner_crud.create_partner(db, partner_in)
        return created
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Could not create partner. Possibly duplicate or invalid fields.")
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=List[PartnerRead])
async def get_partners(
    db: AsyncSession = Depends(get_db)
):
    try:
        items = await partner_crud.get_partners(db)
        return items
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{partner_id}", response_model=PartnerRead)
async def get_partner(
    partner_id: int = Path(..., gt=0, example=1, description="Partner ID"),
    db: AsyncSession = Depends(get_db)
):
    try:
        partner = await partner_crud.get_partner(db, partner_id)
        if not partner:
            raise HTTPException(status_code=404, detail="Partner not found")
        return partner
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{partner_id}", response_model=PartnerRead)
async def update_partner(
    partner_id: int = Path(..., gt=0, example=1, description="Partner ID"),
    partner_in: PartnerUpdate = Body(..., description="Partner data to update"),
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(get_current_admin_user)
):
    try:
        updated = await partner_crud.update_partner(db, partner_id, partner_in.dict(exclude_unset=True))
        if not updated:
            raise HTTPException(status_code=404, detail="Partner not found")
        return updated
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Could not update partner. Possibly duplicate or invalid fields.")
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{partner_id}", response_model=Message)
async def delete_partner(
    partner_id: int = Path(..., gt=0, example=1, description="Partner ID"),
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(get_current_admin_user)
):
    try:
        deleted = await partner_crud.delete_partner(db, partner_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Partner not found")
        return {"success": True, "message": "Partner deleted successfully"}
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Could not delete partner. Possibly dependent records exist.")
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")