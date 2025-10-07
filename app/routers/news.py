from fastapi import APIRouter, Depends, UploadFile, Form, Body, Path, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.db import get_db
from app.core.deps import get_current_user  # JWT auth
from app.schemas.schemas import NewsCreate, NewsUpdate, NewsRead, Message
from app.services import news_service as crud_news
from app.core.uploads import save_uploaded_file, update_entity  # наш универсальный аплоудер

router = APIRouter(prefix="/news", tags=["news"])

# ---------------- CREATE ----------------
@router.post("/", response_model=NewsRead, status_code=status.HTTP_201_CREATED)
async def create_news(
    title: str = Form(...),
    content: str = Form(...),
    file: Optional[UploadFile] = None,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),  # JWT только здесь
):
    file_path = None
    if file:
        file_path = await save_uploaded_file(file, sub_dir="news_files")

    news_in = NewsCreate(
        title=title,
        content=content,
        file_path=file_path or ""
    )
    try:
        return await crud_news.create_news(db, news_in)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка создания новости: {e}")


# ---------------- UPDATE ----------------
@router.put("/{news_id}", response_model=NewsRead)
async def update_news(
    news_id: int = Path(..., gt=0),
    news_in: NewsUpdate = Body(...),
    file: Optional[UploadFile] = None,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),  # JWT только здесь
):
    return await update_entity(
        db=db,
        entity_id=news_id,
        entity_in=news_in,
        crud_update_func=crud_news.update_news,
        file=file,
        file_sub_dir="news_files",
    )


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
    user: dict = Depends(get_current_user),  # JWT только здесь
):
    deleted = await crud_news.delete_news(db, news_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="News not found")
    return {"success": True, "message": "News deleted successfully."}
