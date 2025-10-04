from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, Form, Path, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.schemas.schemas import ApplicationCreate, ApplicationUpdate, ApplicationRead, Message
from app.services import application_service as application_crud
from app.core.db import get_db
from app.core.deps import get_current_admin_user

router = APIRouter(prefix="/applications", tags=["applications"])

# ---------------- CREATE ----------------
@router.post("/", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
async def create_application(
    vacancy_id: int = Form(...),
    name: str = Form(...),
    surname: str = Form(...),
    email: str = Form(...),
    phone_number: str = Form(...),
    portfolio_file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    application_in = ApplicationCreate(
        vacancy_id=vacancy_id,
        name=name,
        surname=surname,
        email=email,
        phone_number=phone_number
    )
    try:
        created = await application_crud.create_application(db, application_in.dict(), [portfolio_file] if portfolio_file else None)
        return created
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Could not create application. Possibly duplicate or invalid fields.")
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

# ---------------- READ ALL ----------------
@router.get("/", response_model=List[ApplicationRead])
async def list_applications(
    vacancy_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(get_current_admin_user)
):
    try:
        items = await application_crud.get_applications(db, vacancy_id)
        return items
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

# ---------------- READ ONE ----------------
@router.get("/{application_id}", response_model=ApplicationRead)
async def get_application(
    application_id: int = Path(..., gt=0, description="Application ID"),
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(get_current_admin_user)
):
    try:
        app_obj = await application_crud.get_application(db, application_id)
        if not app_obj:
            raise HTTPException(status_code=404, detail="Application not found")
        return app_obj
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

# ---------------- UPDATE ----------------
@router.put("/{application_id}", response_model=ApplicationRead)
async def update_application(
    application_id: int = Path(..., gt=0, description="Application ID"),
    name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone_number: Optional[str] = Form(None),
    portfolio_file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(get_current_admin_user)
):
    application_in = ApplicationUpdate(
        name=name,
        email=email,
        phone_number=phone_number
    )
    try:
        updated = await application_crud.update_application(db, application_id, application_in.dict(exclude_unset=True), [portfolio_file] if portfolio_file else None)
        if not updated:
            raise HTTPException(status_code=404, detail="Application not found")
        return updated
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Could not update application. Possibly duplicate or invalid fields.")
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

# ---------------- DELETE ----------------
@router.delete("/{application_id}", response_model=Message)
async def delete_application(
    application_id: int = Path(..., gt=0, description="Application ID"),
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(get_current_admin_user)
):
    try:
        deleted = await application_crud.delete_application(db, application_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Application not found")
        return {"success": True, "message": "Application deleted successfully"}
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
