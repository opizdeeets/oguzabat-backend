# app/routers/project.py
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Form,
    UploadFile,
    File,
    Path,
    Query,
)
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.db import get_db
from app.core.deps import get_current_admin_user
from app.schemas.schemas import ProjectCreate, ProjectUpdate, ProjectRead, ProjectStatus
from app.services import project_service
from app.core.uploads import save_uploaded_file

router = APIRouter(prefix="/projects", tags=["projects"])


# ---------- CREATE ----------
@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    company_id: int = Form(...),
    name: str = Form(...),
    type: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    status: Optional[ProjectStatus] = Form("Pending"),
    short_description: Optional[str] = Form(None),
    full_description: Optional[str] = Form(None),
    gallery_files: Optional[List[UploadFile]] = File(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_admin_user),
):
    """
    Создание проекта.
    Дата открытия (`opened_date`) выставляется автоматически в модели.
    """
    gallery_paths: List[str] = []

    # ✅ Асинхронное сохранение файлов (в отличие от вашей версии)
    if gallery_files:
        for file in gallery_files:
            path = await save_uploaded_file(file, "projects")
            gallery_paths.append(path)

    project_in = ProjectCreate(
        company_id=company_id,
        name=name,
        type=type,
        location=location,
        status=status,
        short_description=short_description,
        full_description=full_description,
    )

    project = await project_service.create_project(db, project_in, gallery_paths)
    return project


# ---------- READ ----------
@router.get("/", response_model=List[ProjectRead])
async def get_projects(
    company_id: Optional[int] = Query(None, description="ID компании для фильтрации"),
    db: AsyncSession = Depends(get_db),
):
    """
    Получение всех проектов или фильтрация по company_id.
    """
    return await project_service.get_projects(db, company_id)


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: int = Path(..., gt=0, description="ID проекта"),
    db: AsyncSession = Depends(get_db),
):
    """
    Получение проекта по ID.
    """
    project = await project_service.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


# ---------- UPDATE ----------
@router.put("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: int = Path(..., gt=0, description="ID проекта"),
    name: Optional[str] = Form(None),
    type: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    status: Optional[ProjectStatus] = Form(None),
    short_description: Optional[str] = Form(None),
    full_description: Optional[str] = Form(None),
    new_gallery_files: Optional[List[UploadFile]] = File(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_admin_user),
):
    """
    Обновление данных проекта.
    Если передана новая галерея, старая будет заменена.
    """
    gallery_paths: Optional[List[str]] = None

    if new_gallery_files:
        gallery_paths = []
        for file in new_gallery_files:
            path = await save_uploaded_file(file, "projects")
            gallery_paths.append(path)

    project_in = ProjectUpdate(
        name=name,
        type=type,
        location=location,
        status=status,
        short_description=short_description,
        full_description=full_description,
    )

    updated_project = await project_service.update_project(
        db, project_id, project_in, gallery_paths
    )
    if not updated_project:
        raise HTTPException(status_code=404, detail="Project not found")

    return updated_project


# ---------- DELETE ----------
@router.delete("/{project_id}", response_model=bool)
async def delete_project(
    project_id: int = Path(..., gt=0, description="ID проекта"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_admin_user),
):
    """
    Удаляет проект и связанные изображения.
    """
    deleted = await project_service.delete_project(db, project_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found")
    return True
