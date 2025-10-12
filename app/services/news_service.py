from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import UploadFile, HTTPException
from typing import Optional
import traceback

from app.models.models import News
from app.schemas.schemas import NewsCreate, NewsUpdate
from app.core.uploads import save_uploaded_file, delete_uploaded_file

# ---------------- CREATE ----------------
async def create_news(
    db: AsyncSession,
    news_in: NewsCreate,
    file: Optional[UploadFile] = None
) -> News:
    """
    Создаёт новость с изображением.
    Дата теперь устанавливается автоматически на уровне БД.
    """
    try:
        image_path = None
        if file:
            image_path = await save_uploaded_file(file, sub_dir="news_files")

        db_news = News(
            title=news_in.title,
            short_description=news_in.short_description,
            full_text=news_in.full_text,
            image_path=image_path or news_in.image_path
        )

        db.add(db_news)
        await db.commit()
        await db.refresh(db_news)
        return db_news

    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Ошибка целостности данных")
    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка базы данных")
    except Exception as e:
        await db.rollback()
        print("Error in create_news:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

# ---------------- READ ONE ----------------
async def get_news(db: AsyncSession, news_id: int) -> Optional[News]:
    try:
        result = await db.execute(select(News).where(News.id == news_id))
        return result.scalars().first()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Ошибка базы данных")

# ---------------- READ ALL ----------------
async def get_news_list(
    db: AsyncSession,
    search: Optional[str] = None,
    sort: str = "date_desc"
) -> list[News]:
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

        stmt = stmt.order_by(News.date.asc() if sort == "date_asc" else News.date.desc())
        result = await db.execute(stmt)
        return result.scalars().all()

    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Ошибка базы данных")

# ---------------- UPDATE ----------------
async def update_news(
    db: AsyncSession,
    news_id: int,
    news_in: NewsUpdate,
    file: Optional[UploadFile] = None
) -> Optional[News]:
    try:
        result = await db.execute(select(News).where(News.id == news_id))
        db_news = result.scalars().first()
        if not db_news:
            raise HTTPException(status_code=404, detail="Новость не найдена")

        update_data = news_in.dict(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_news, field, value)

        if file:
            if db_news.image_path:
                try:
                    await delete_uploaded_file(db_news.image_path)
                except FileNotFoundError:
                    pass
            db_news.image_path = await save_uploaded_file(file, sub_dir="news_files")

        await db.commit()
        await db.refresh(db_news)
        return db_news

    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Ошибка целостности данных")
    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка базы данных")
    except Exception as e:
        await db.rollback()
        print("Error in update_news:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

# ---------------- DELETE ----------------
async def delete_news(db: AsyncSession, news_id: int) -> bool:
    try:
        result = await db.execute(select(News).where(News.id == news_id))
        db_news = result.scalars().first()
        if not db_news:
            return False

        if db_news.image_path:
            try:
                await delete_uploaded_file(db_news.image_path)
            except FileNotFoundError:
                pass

        await db.delete(db_news)
        await db.commit()
        return True

    except Exception as e:
        await db.rollback()
        print("Error in delete_news:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")
