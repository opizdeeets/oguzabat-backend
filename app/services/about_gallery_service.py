from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import UploadFile, HTTPException, status
from typing import List, Optional

from sqlalchemy.orm import selectinload

from app.models.models import AboutUsGallery, AboutUsImage
from app.schemas.schemas import AboutUsGalleryRead
from app.core.uploads import save_uploaded_file, delete_uploaded_file, save_uploaded_files

GALLERY_SUBDIR = "about_us_gallery"
MAX_IMAGE_SIZE_MB = 7

# ---------------- CRUD ----------------
async def get_aboutusgallery(db: AsyncSession) -> AboutUsGallery:
    """
    Возвращает единственную запись галереи с вложенными изображениями.
    """
    result = await db.execute(select(AboutUsGallery).options(selectinload(AboutUsGallery.images)))
    gallery = result.scalars().first()
    if not gallery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AboutUsGallery not found"
        )
    # Загрузка изображений
    await db.refresh(gallery)
    return gallery


async def create_aboutusgallery_images(
    db: AsyncSession,
    files: List[UploadFile]
) -> List[AboutUsImage]:
    """
    Загружает несколько изображений и привязывает их к единственной записи галереи.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    gallery = await get_aboutusgallery(db)

    saved_images = []
    for file in files:
        path = await save_uploaded_file(file, GALLERY_SUBDIR, max_mb=MAX_IMAGE_SIZE_MB)
        image = AboutUsImage(
            gallery_id=gallery.id,
            image_path=path
        )
        db.add(image)
        saved_images.append(image)

    try:
        await db.commit()
        for img in saved_images:
            await db.refresh(img)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {e}"
        )

    return saved_images


async def update_about_us_gallery(
    db: AsyncSession,
    gallery_id: int,
    update_data: dict,
    files: Optional[List[UploadFile]] = None
) -> AboutUsGallery:
    # 1️⃣ Получаем галерею
    result = await db.execute(select(AboutUsGallery).filter(AboutUsGallery.id == gallery_id))
    gallery = result.scalars().first()
    if not gallery:
        raise HTTPException(status_code=404, detail=f"Gallery with id={gallery_id} not found")

    # 2️⃣ Обновляем поля сущности
    for key, value in update_data.items():
        setattr(gallery, key, value)

    # 3️⃣ Обрабатываем загруженные изображения
    if files:
        try:
            saved_paths = await save_uploaded_files(files, GALLERY_SUBDIR, max_mb=7)
            for path in saved_paths:
                new_image = AboutUsImage(image_path=path, gallery_id=gallery.id)
                db.add(new_image)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"File upload error: {e}")

    # 4️⃣ Коммит изменений
    try:
        await db.commit()
        await db.refresh(gallery)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    return gallery


async def delete_aboutusgallery_image(
    db: AsyncSession,
    image_id: int
) -> bool:
    """
    Удаляет изображение из галереи и файл с диска.
    """
    result = await db.execute(select(AboutUsImage).filter(AboutUsImage.id == image_id))
    image = result.scalars().first()
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image with id={image_id} not found"
        )

    try:
        await delete_uploaded_file(image.image_path)
        await db.delete(image)
        await db.commit()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting image: {e}"
        )

    return True