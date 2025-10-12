
from typing import List, Optional
from datetime import datetime
from fastapi import (
    APIRouter, Depends, UploadFile, Form, Path, status, HTTPException
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.deps import get_current_user
from app.schemas.schemas import NewsCreate, NewsUpdate, NewsRead
from app.services import news_service
from app.core.uploads import save_uploaded_file

router = APIRouter(prefix="/news", tags=["News"])


# ---------- CREATE ----------
@router.post("/", response_model=NewsRead, status_code=status.HTTP_201_CREATED)
async def create_news(
    title: str = Form(...),
    short_description: str = Form(...),
    full_text: str = Form(...),
    file: Optional[UploadFile] = None,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """
    Создать новость. Дата публикации выставляется автоматически.
    """
    image_path = None
    if file:
        image_path = await save_uploaded_file(file, "news_images")

    news_in = NewsCreate(
        title=title,
        short_description=short_description,
        full_text=full_text,
        image_path=image_path
    )

    try:
        news = await news_service.create_news(db=db, news_in=news_in)
        return news
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка создания новости: {e}")


# ---------- UPDATE ----------
@router.put("/{news_id}", response_model=NewsRead)
async def update_news(
    news_id: int = Path(..., gt=0),
    title: Optional[str] = Form(None),
    short_description: Optional[str] = Form(None),
    full_text: Optional[str] = Form(None),
    file: Optional[UploadFile] = None,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """
    Обновить новость. Дата редактирования устанавливается автоматически.
    """
    image_path = None
    if file:
        image_path = await save_uploaded_file(file, "news_images")

    news_in = NewsUpdate(
        title=title,
        short_description=short_description,
        full_text=full_text,
        image_path=image_path
    )

    news = await news_service.update_news(db=db, news_id=news_id, news_in=news_in)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")

    return news


# ---------- READ LIST ----------
@router.get("/", response_model=List[NewsRead])
async def list_news(
    search: Optional[str] = None,
    sort: str = "date_desc",
    db: AsyncSession = Depends(get_db),
):
    """
    Получить список новостей с поиском и сортировкой.
    """
    try:
        return await news_service.get_news_list(db, search=search, sort=sort)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения списка новостей: {e}")


# ---------- READ SINGLE ----------
@router.get("/{news_id}", response_model=NewsRead)
async def get_news(
    news_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
):
    """
    Получить одну новость по ID.
    """
    news = await news_service.get_news(db, news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    return news


# ---------- DELETE ----------
@router.delete("/{news_id}", response_model=bool)
async def delete_news(
    news_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """
    Удалить новость по ID.
    """
    deleted = await news_service.delete_news(db, news_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="News not found")
    return True
