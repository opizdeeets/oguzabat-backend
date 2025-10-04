from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import List, Optional

from app.core.db import get_db
from app.core.deps import get_current_admin_user
from app.models.models import News
from app.schemas.schemas import NewsCreate, NewsUpdate, NewsRead, Message
from app.services import news_service as crud_news

router = APIRouter(prefix="/news", tags=["news"])

@router.post("/", response_model=NewsRead, status_code=status.HTTP_201_CREATED)
async def create_news(  # ✅ news с маленькой
    news_in: NewsCreate,  # ✅ news_in с маленькой
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(get_current_admin_user)
):
    """
    Create a new news article
    """
    try:
        created = await crud_news.create_news(db, news_in)
        return created
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Could not create news. Possibly duplicate or invalid fields.")
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=List[NewsRead])
async def list_news(  # ✅ list_news
    search: Optional[str] = Query(None),
    sort: str = Query("date_desc"),
    db: AsyncSession = Depends(get_db)
): 
    try:
        items = await crud_news.get_news_list(db, search=search, sort=sort)
        return items
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{news_id}", response_model=NewsRead)  # ✅ {news_id}
async def get_news(
    news_id: int = Path(..., gt=0, example=1, description="News ID"),  # ✅ news_id
    db: AsyncSession = Depends(get_db)
):
    try:
        news = await crud_news.get_news(db, news_id)
        if not news:
            raise HTTPException(status_code=404, detail="News not found")
        return news
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{news_id}", response_model=NewsRead)  # ✅ {news_id}
async def update_news(  # ✅ update_news
    news_id: int = Path(..., gt=0, example=1, description="News ID"),
    news_in: NewsUpdate = Body(..., description="News data to update"),
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(get_current_admin_user)
):
    try:
        updated = await crud_news.update_news(db, news_id, news_in.dict(exclude_unset=True))
        if not updated:
            raise HTTPException(status_code=404, detail="News not found")
        return updated
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Could not update news. Possibly duplicate or invalid fields.")
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{news_id}", response_model=Message)  # ✅ {news_id}
async def delete_news(  # ✅ delete_news
    news_id: int = Path(..., gt=0, example=1, description="News ID"),
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(get_current_admin_user)
):
    try:
        deleted = await crud_news.delete_news(db, news_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="News not found")
        return {"success": True, "message": "News deleted successfully."}
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Could not delete news. Possibly dependent records exist.")
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")