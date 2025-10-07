from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import delete
from fastapi import UploadFile, HTTPException
from typing import List, Optional
import traceback

from app.models.models import News, NewsFile
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
    """
    try:
        file_objs = []
        if files:
            if not isinstance(files, list):
                files = [files]
            for f in files:
                path = await save_uploaded_file(f, sub_dir="news")
                file_objs.append(NewsFile(file_url=path))

        db_news = News(**news_in.dict(), files=file_objs)
        db.add(db_news)
        await db.commit()
        await db.refresh(db_news)
        return db_news
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
            .options()  # Можно добавить selectinload(News.files) если есть relationships
        )
        return result.scalars().first()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")

# ---------------- READ ALL ----------------
async def get_news_list(db: AsyncSession, search: Optional[str] = None, sort: str = "date_desc") -> List[News]:
    try:
        stmt = select(News)
        if search:
            search_term = f"%{search}%"
            stmt = stmt.where(News.title.ilike(search_term) | News.short_description.ilike(search_term))

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
    files: Optional[List[UploadFile]] = None
) -> Optional[News]:
    """
    Обновляет поля новости и добавляет новые файлы.
    Старые файлы остаются, удалять их отдельно через delete_file или replace_uploaded_file.
    """
    try:
        result = await db.execute(select(News).where(News.id == news_id))
        db_news = result.scalars().first()
        if not db_news:
            return None

        update_data = news_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_news, field, value)

        # Новые файлы
        if files:
            if not isinstance(files, list):
                files = [files]
            for f in files:
                path = await save_uploaded_file(f, sub_dir="news")
                db_news.files.append(NewsFile(file_url=path))

        await db.commit()
        await db.refresh(db_news)
        return db_news
    except Exception as e:
        await db.rollback()
        print("Error in update_news:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")

# ---------------- DELETE ----------------
async def delete_news(db: AsyncSession, news_id: int) -> bool:
    """
    Удаляет новость и все прикреплённые файлы с диска.
    """
    try:
        result = await db.execute(select(News).where(News.id == news_id))
        db_news = result.scalars().first()
        if not db_news:
            return False

        # Удаляем файлы
        for f in db_news.files:
            await delete_uploaded_file(f.file_url)

        await db.delete(db_news)
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        print("Error in delete_news:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")
