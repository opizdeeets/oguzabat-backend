from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, Form, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import List, Optional

from app.core.db import get_db
from app.core.deps import get_current_user  # JWT авторизация
from app.models.models import AboutGallery, SortOrder
from app.schemas.schemas import AboutGalleryCreate, AboutGalleryUpdate, AboutGalleryRead, Message
from app.services import about_gallery_service as image_crud
from app.core.uploads import save_uploaded_file, replace_uploaded_file

router = APIRouter(prefix="/aboutgallery", tags=["aboutgallery"])

# ---------------- CREATE ----------------
@router.post("/", response_model=AboutGalleryRead, status_code=status.HTTP_201_CREATED)
async def create_image(
    title: str = Form(..., description="Image title"),
    sort_order: int = Form(0, description="Sort order"),
    file: UploadFile = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # JWT защищает эндпоинт
):
    """
    Создает запись изображения для About Us с поддержкой загрузки файла.
    """
    try:
        file_path = await save_uploaded_file(file, sub_dir="about_gallery") if file else None

        image_in = AboutGalleryCreate(title=title, sort_order=sort_order, image_path=file_path)
        created = await image_crud.create_image(db, image_in)
        return created

    except IntegrityError:
        raise HTTPException(status_code=400, detail="Duplicate or invalid fields")
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        print("Error in create_image:", e)
        raise HTTPException(status_code=500, detail="Internal server error")

# ---------------- LIST ----------------
@router.get("/", response_model=List[AboutGalleryRead])
async def get_images(
    sort: SortOrder = Query(SortOrder.order_asc),
    db: AsyncSession = Depends(get_db)
):
    """Возвращает список изображений с сортировкой."""
    try:
        items = await image_crud.get_images(db, sort=sort.value)
        return items
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

# ---------------- GET SINGLE ----------------
@router.get("/{image_id}", response_model=AboutGalleryRead)
async def get_image(
    image_id: int = Path(..., gt=0, description="Image ID"),
    db: AsyncSession = Depends(get_db)
):
    """Возвращает одно изображение по ID."""
    try:
        image = await image_crud.get_image(db, image_id)
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")
        return image
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

# ---------------- UPDATE ----------------
@router.put("/{image_id}", response_model=AboutGalleryRead)
async def update_image(
    image_id: int = Path(..., gt=0, description="Image ID"),
    title: Optional[str] = Form(None, description="Image title"),
    sort_order: Optional[int] = Form(None, description="Sort order"),
    file: UploadFile = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Обновляет запись изображения и при необходимости заменяет файл.
    """
    try:
        # Подготавливаем dict для обновления
        updated_data = {}
        if title is not None:
            updated_data["title"] = title
        if sort_order is not None:
            updated_data["sort_order"] = sort_order

        # Обновление с заменой файла
        if file:
            updated_data["image_path"] = await replace_uploaded_file(
                old_file_url=(await image_crud.get_image(db, image_id)).image_path,
                new_file=file,
                sub_dir="about_gallery"
            )

        updated = await image_crud.update_image(db, image_id, updated_data)
        if not updated:
            raise HTTPException(status_code=404, detail="Image not found")
        return updated

    except IntegrityError:
        raise HTTPException(status_code=400, detail="Duplicate or invalid fields")
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        print("Error in update_image:", e)
        raise HTTPException(status_code=500, detail="Internal server error")

# ---------------- DELETE ----------------
@router.delete("/{image_id}", response_model=Message)
async def delete_image(
    image_id: int = Path(..., gt=0, description="Image ID"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Удаляет изображение и его файл."""
    try:
        image = await image_crud.get_image(db, image_id)
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")

        if image.image_path:
            from app.core.uploads import delete_uploaded_file
            await delete_uploaded_file(image.image_path)

        deleted = await image_crud.delete_image(db, image_id)
        return {"success": True, "message": "Image deleted successfully"}

    except IntegrityError:
        raise HTTPException(status_code=400, detail="Could not delete. Dependent resources exist")
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        print("Error in delete_image:", e)
        raise HTTPException(status_code=500, detail="Internal server error")
