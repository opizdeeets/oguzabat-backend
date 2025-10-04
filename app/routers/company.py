from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import List, Optional

from app.core.db import get_db
from app.core.deps import get_current_admin_user
from app.models.models import Company
from app.schemas.schemas import CompanyCreate, CompanyUpdate, CompanyRead, Message
from app.services import company_service as crud_company


router = APIRouter(
    prefix="/companies",
    tags=["companies"]
)


@router.post("/", response_model=CompanyRead, status_code= status.HTTP_201_CREATED)
async def create_company(
    company_in: CompanyCreate,
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(get_current_admin_user)
):
    """
    Create a new company
    """
    try:
        created = await crud_company.create_company(db, company_in)
        return created
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not create company. Possibly duplicate or invalid fields.")
    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    
@router.get("/", 
    response_model=List[CompanyRead],
    responses={
        500: {"model": Message, "description": "Internal server error"}
    }
)
async def list_companies(
    categories: Optional[List[str]] = Query(None, description="Filter by categories"),
    db: AsyncSession = Depends(get_db)
): 
    try:
        items = await crud_company.get_companies(db, categories=categories)
        return items
    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/{company_id}", 
    response_model=CompanyRead,
    responses={
        404: {"model": Message, "description": "Company not found"},
        500: {"model": Message, "description": "Internal server error"}
    }
)
async def retrieve_company(
    company_id: int = Path(..., gt=0, example=1, description="Company ID"),
    db: AsyncSession = Depends(get_db)
):
    try:
        company = await crud_company.get_company(db, company_id)
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        return company
    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.put("/{company_id}", 
    response_model=CompanyRead,
    responses={
        404: {"model": Message, "description": "Company not found"},
        400: {"model": Message, "description": "Duplicate or invalid data"}, 
        500: {"model": Message, "description": "Internal server error"}
    }
)
async def update_company(
    company_id: int = Path(..., gt=0, example=1, description="Company ID"),  # ✅ ПЕРВЫЙ ПАРАМЕТР
    company_in: CompanyUpdate = Body(..., description="Company data to update"),                                         # ✅ ПОТОМ BODY
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(get_current_admin_user)
):
    try:
        updated = await crud_company.update_company(db, company_id, company_in.dict(exclude_unset=True))
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        return updated
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not update company. Possibly duplicate or invalid fields.")
    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.delete("/{company_id}", response_model=Message)
async def delete_company(
    company_id: int = Path(..., gt=0, example=1, description="Company ID"),
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(get_current_admin_user)
):
    try:
        deleted = await crud_company.delete_company(db, company_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        return {"success": True, "message": "Company deleted successfully."}
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not delete company. Possibly dependent records exist.")
    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
