from fastapi import (
    APIRouter, Depends, HTTPException, status,
    Query, Path, Form, UploadFile, File
)
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from app.core.db import get_db
from app.core.deps import get_current_admin_user
from app.schemas.schemas import ProjectCreate, ProjectUpdate, ProjectRead, Message
from app.services import project_service as crud_project

router = APIRouter(prefix="/projects", tags=["projects"])

# ---------------- CREATE ----------------
@router.post(
    "/projects/",
    response_model=ProjectRead,
    status_code=201
)
async def create_project(
    company_id: int = Form(...),
    name: str = Form(...),
    type: str = Form(...),
    location: str = Form(...),
    opened_date: Optional[datetime] = Form(None),
    status: str = Form("Pending"),
    short_description: str = Form(...),
    full_description: str = Form(...),
    gallery_files: List[UploadFile] = File([]),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_admin_user),
):
    # Создаем объект Pydantic, валидатор внутри конвертирует строку в datetime
    project_in = ProjectCreate(
        company_id=company_id,
        name=name,
        type=type,
        location=location,
        opened_date=opened_date,
        status=status,
        short_description=short_description,
        full_description=full_description,
    )

    gallery_paths = [f"uploads/project_gallery/{file.filename}" for file in gallery_files]

    project = await crud_project.create_project(db, project_in, gallery_paths)
    return project

# ---------------- READ ALL ----------------
@router.get("/", response_model=List[ProjectRead])
async def get_projects(
    company_id: Optional[int] = Query(None, description="Filter by company ID"),
    db: AsyncSession = Depends(get_db)
):
    return await crud_project.get_projects(db, company_id)

# ---------------- READ ONE ----------------
@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db)
):
    project = await crud_project.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project

# ---------------- UPDATE ----------------
@router.put("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: int = Path(..., gt=0),
    name: Optional[str] = Form(None),
    type: Optional[str] = Form(None),
    company_id: Optional[int] = Form(None),
    opened_date: Optional[datetime] = Form(None),
    short_description: Optional[str] = Form(None),
    full_description: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    status: Optional[str] = Form(None),
    new_gallery_files: Optional[List[UploadFile]] = None,
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(get_current_admin_user)
):
    project_in = ProjectUpdate(
        name=name,
        type=type,
        company_id=company_id,
        opened_date=opened_date,
        short_description=short_description,
        full_description=full_description,
        location=location,
        status=status
    )
    updated = await crud_project.update_project(db, project_id, project_in, new_gallery_files)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return updated

# ---------------- DELETE ----------------
@router.delete("/{project_id}", response_model=Message)
async def delete_project(
    project_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(get_current_admin_user)
):
    deleted = await crud_project.delete_project(db, project_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return {"success": True, "message": "Project deleted successfully"}
