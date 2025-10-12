from fastapi import APIRouter, Depends, UploadFile, HTTPException, status, Form, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.db import get_db
from app.schemas.schemas import AboutUsGalleryRead
from app.services import about_gallery_service

router = APIRouter(
    prefix="/aboutusgallery",
    tags=["AboutUsGallery"]
)


@router.get("/", response_model=AboutUsGalleryRead)
async def read_gallery(db: AsyncSession = Depends(get_db)):
    """
    Получить единственную запись галереи с вложенными изображениями.
    """
    gallery = await about_gallery_service.get_aboutusgallery(db)
    return gallery


@router.post("/images/", response_model=AboutUsGalleryRead)
async def upload_gallery_images(
    files: List[UploadFile] = File(..., description="Выберите изображения для галереи"),
    db: AsyncSession = Depends(get_db)
):
    """
    Загрузить несколько изображений в галерею.
    """
    try:
        images = await about_gallery_service.create_aboutusgallery_images(db, files)
        # Возвращаем полную запись галереи с новыми изображениями
        gallery = await about_gallery_service.get_aboutusgallery(db)
        return gallery
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {e}"
        )


@router.put("/{gallery_id}", response_model=AboutUsGalleryRead)
async def update_gallery(
    gallery_id: int,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None, description="Новые изображения для галереи"),
    db: AsyncSession = Depends(get_db)
):
    """
    Обновить поля галереи и добавить новые изображения.
    """
    update_data = {}
    if title is not None:
        update_data["title"] = title
    if description is not None:
        update_data["description"] = description

    try:
        # Передаем новые файлы прямо в update_about_us_gallery
        gallery = await about_gallery_service.update_about_us_gallery(
            db, gallery_id, update_data, files=files
        )
        # Возвращаем обновленную галерею с изображениями
        gallery = await about_gallery_service.get_aboutusgallery(db)
        return gallery

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {e}"
        )




@router.delete("/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_gallery_image(
    image_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Удалить отдельное изображение из галереи.
    """
    try:
        await about_gallery_service.delete_aboutusgallery_image(db, image_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {e}"
        )
    return True