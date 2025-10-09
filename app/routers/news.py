from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, UploadFile, Form, Path, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.deps import get_current_user
from app.schemas.schemas import NewsCreate, NewsUpdate, NewsRead, Message
from app.services import news_service as crud_news
from app.core.uploads import update_entity

router = APIRouter(prefix="/news", tags=["news"])

# ---------------- CREATE ----------------
@router.post("/", response_model=NewsRead, status_code=status.HTTP_201_CREATED)
async def create_news(
    title: str = Form(...),
    short_description: str = Form(...),
    full_text: str = Form(...),
    date: Optional[datetime] = Form(None),
    file: Optional[UploadFile] = None,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    news_in = NewsCreate(
        title=title,
        short_description=short_description,
        full_text=full_text,
        date=date or datetime.utcnow()
    )
    try:
        return await crud_news.create_news(db=db, news_in=news_in, file=file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка создания новости: {e}")


# ---------------- UPDATE ----------------
@router.put("/{news_id}", response_model=NewsRead)
async def update_news(
    news_id: int = Path(..., gt=0),
    title: Optional[str] = Form(None),
    short_description: Optional[str] = Form(None),
    full_text: Optional[str] = Form(None),
    date: Optional[datetime] = Form(None),
    file: Optional[UploadFile] = None,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    news_in = NewsUpdate(
        title=title,
        short_description=short_description,
        full_text=full_text,
        date=date
    )
    return await crud_news.update_news(db=db, news_id=news_id, news_in=news_in, file=file)


# ---------------- GET LIST ----------------
@router.get("/", response_model=List[NewsRead])
async def list_news(
    search: Optional[str] = None,
    sort: str = "date_desc",
    db: AsyncSession = Depends(get_db)
):
    try:
        return await crud_news.get_news_list(db, search=search, sort=sort)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения списка новостей: {e}")


# ---------------- GET SINGLE ----------------
@router.get("/{news_id}", response_model=NewsRead)
async def get_news(news_id: int = Path(..., gt=0), db: AsyncSession = Depends(get_db)):
    news = await crud_news.get_news(db, news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    return news


# ---------------- DELETE ----------------
@router.delete("/{news_id}", response_model=Message)
async def delete_news(
    news_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    deleted = await crud_news.delete_news(db, news_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="News not found")
    return {"success": True, "message": "News deleted successfully."}
