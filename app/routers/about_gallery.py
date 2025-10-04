from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import List, Optional

from app.core.db import get_db
from app.core.deps import get_current_admin_user
from app.models.models import AboutGallery, SortOrder
from app.schemas.schemas import AboutGalleryCreate, AboutGalleryUpdate, AboutGalleryRead, Message
from app.services import about_gallery_service as image_crud

router = APIRouter(prefix="/aboutgallery", tags=["aboutgallery"])

@router.post("/", response_model=AboutGalleryRead, status_code=status.HTTP_201_CREATED)
async def create_image(
    image_in: AboutGalleryCreate = Body(..., description="Image data to create"),
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(get_current_admin_user)
):
    try:
        created = await image_crud.create_image(db, image_in)
        return created
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Could not create image. Possibly duplicate or invalid fields.")
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
    

@router.get("/", response_model=List[AboutGalleryRead])
async def get_images(
    sort: SortOrder = Query(SortOrder.order_asc),
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(get_current_admin_user)
):
    try:
        items = await image_crud.get_images(db, sort=sort.value)
        return items
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.get("/{image_id}", response_model=AboutGalleryRead)
async def get_image(
    image_id: int = Path(..., gt=0, example=1, description="Image ID"),
    db: AsyncSession = Depends(get_db)
):
    try:
        image = await image_crud.get_image(db, image_id)
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")
        return image
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error") 

@router.put("/{image_id}", response_model=AboutGalleryRead)
async def update_image(
    image_id: int = Path(..., gt=0, example=1, description="Image ID"),
    image_in: AboutGalleryUpdate = Body(..., description="Image data to update"),
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(get_current_admin_user)
):
    try:
        updated = await image_crud.update_image(db, image_id, image_in.dict(exclude_unset=True))
        if not updated:
            raise HTTPException(status_code=404, detail="Image not found")
        return updated
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Could not update image. Possibly duplicate or invalid fields.")
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{image_id}", response_model=Message)
async def delete_image(
    image_id: int = Path(..., gt=0, example=1, description="Image ID"),
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(get_current_admin_user)
):
    try:
        deleted = await image_crud.delete_image(db, image_id)
        if not deleted:
             raise HTTPException(status_code=404, detail="Image not found")
        return {"success": True, "message": "Image deleted successfully"}
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Could not delete image. Possibly dependent resources exist.")
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")