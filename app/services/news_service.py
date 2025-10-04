from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.models.models import News
from app.schemas.schemas import NewsCreate, NewsUpdate
from typing import List, Optional


# CREATE
async def create_news(db: AsyncSession, news_in: NewsCreate) -> News:
    try:
        db_news = News(**news_in.dict())
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


# READ one
async def get_news(db: AsyncSession, news_id: int) -> Optional[News]:
    try:
        result = await db.execute(select(News).where(News.id == news_id))
        return result.scalars().first()
    except SQLAlchemyError:
        raise


# READ all (БЕЗ пагинации)
async def get_news_list(db: AsyncSession, search: Optional[str] = None, sort: str = "date_desc") -> List[News]:
    try:
        stmt = select(News)

        if search:
            search_term = f"%{search}%"
            stmt = stmt.where(
                News.title.ilike(search_term) |
                News.short_description.ilike(search_term))
            
        if sort not in ["date_asc", "date_desc"]:
            sort = "date_desc"
        
        if sort == "date_asc":
            stmt = stmt.order_by(News.date.asc())
        else:
            stmt = stmt.order_by(News.date.desc())

        result = await db.execute(stmt)
        return result.scalars().all()
    except SQLAlchemyError:
        raise


# UPDATE
async def update_news(db: AsyncSession, news_id: int, news_in: NewsUpdate) -> Optional[News]:
    try:
        result = await db.execute(select(News).where(News.id == news_id))
        db_news = result.scalars().first()

        if not db_news:
            return None

        update_data = news_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_news, field, value)

        await db.commit()
        await db.refresh(db_news)
        return db_news
    except IntegrityError:
        await db.rollback()
        raise
    except SQLAlchemyError:
        await db.rollback()
        raise


# DELETE
async def delete_news(db: AsyncSession, news_id: int) -> bool:
    try:
        result = await db.execute(delete(News).where(News.id == news_id))  # Эффективное удаление
        await db.commit()
        return result.rowcount > 0
    except SQLAlchemyError:
        await db.rollback()
        raise