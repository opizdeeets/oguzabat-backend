from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import UploadFile, HTTPException
from typing import List, Optional
import traceback

from app.models.models import News
from app.schemas.schemas import NewsCreate, NewsUpdate
from app.core.uploads import save_uploaded_file, delete_uploaded_file

# ---------------- CREATE ----------------
async def create_news(
    db: AsyncSession,
    news_in: NewsCreate,
    files: Optional[List[UploadFile]] = None
) -> News:
    """
    Создаёт новость с поддержкой нескольких файлов (изображения, PDF).
    gallery - просто список ссылок.
    """
    try:
        gallery_urls = []
        if files:
            if not isinstance(files, list):
                files = [files]
            for f in files:
                url = await save_uploaded_file(f, sub_dir="news")
                gallery_urls.append(url)

        db_news = News(**news_in.dict(), gallery=gallery_urls)
        db.add(db_news)
        await db.commit()
        await db.refresh(db_news)
        return db_news
    except IntegrityError:
        await db.rollback()
        raise
    except SQLAlchemyError:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        print("Error in create_news:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")

# ---------------- READ ONE ----------------
async def get_news(db: AsyncSession, news_id: int) -> Optional[News]:
    try:
        result = await db.execute(
            select(News).where(News.id == news_id)
        )
        return result.scalars().first()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")

# ---------------- READ ALL ----------------
async def get_news_list(
    db: AsyncSession,
    search: Optional[str] = None,
    sort: str = "date_desc"
) -> List[News]:
    try:
        stmt = select(News)
        if search:
            search_term = f"%{search}%"
            stmt = stmt.where(
                News.title.ilike(search_term) |
                News.short_description.ilike(search_term)
            )

        if sort not in ["date_asc", "date_desc"]:
            sort = "date_desc"

        stmt = stmt.order_by(News.date.asc() if sort=="date_asc" else News.date.desc())
        result = await db.execute(stmt)
        return result.scalars().all()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")

# ---------------- UPDATE ----------------
async def update_news(
    db: AsyncSession,
    news_id: int,
    news_in: NewsUpdate,
    new_files: Optional[List[UploadFile]] = None
) -> Optional[News]:
    try:
        result = await db.execute(select(News).where(News.id == news_id))
        db_news = result.scalars().first()
        if not db_news:
            return None

        update_data = news_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_news, field, value)

        # Добавляем новые файлы в gallery
        if new_files:
            gallery_urls = db_news.gallery.copy() if db_news.gallery else []
            if not isinstance(new_files, list):
                new_files = [new_files]
            for f in new_files:
                url = await save_uploaded_file(f, sub_dir="news")
                gallery_urls.append(url)
            db_news.gallery = gallery_urls

        await db.commit()
        await db.refresh(db_news)
        return db_news
    except IntegrityError:
        await db.rollback()
        raise
    except SQLAlchemyError:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        print("Error in update_news:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")

# ---------------- DELETE ----------------
async def delete_news(db: AsyncSession, news_id: int) -> bool:
    try:
        result = await db.execute(select(News).where(News.id == news_id))
        db_news = result.scalars().first()
        if not db_news:
            return False

        # Удаляем все файлы из gallery
        if db_news.gallery:
            for url in db_news.gallery:
                await delete_uploaded_file(url)

        await db.delete(db_news)
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        print("Error in delete_news:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")
