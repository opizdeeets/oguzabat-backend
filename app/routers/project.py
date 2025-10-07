from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, Form, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import List, Optional

from app.core.db import get_db
from app.core.deps import get_current_user  # JWT авторизация
from app.models.models import Project
from app.schemas.schemas import ProjectCreate, ProjectUpdate, ProjectRead, Message
from app.services import project_service as crud_project
from app.core.uploads import save_uploaded_file, replace_uploaded_file, delete_uploaded_file

router = APIRouter(prefix="/projects", tags=["projects"])

# ---------------- CREATE ----------------
@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    title: str = Form(..., description="Project title"),
    company_id: Optional[int] = Form(None, description="Company ID"),
    file: UploadFile = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # JWT защищает эндпоинт
):
    """
    Создает новый проект с возможностью загрузки изображения.
    """
    try:
        file_path = await save_uploaded_file(file, sub_dir="projects") if file else None
        project_in = ProjectCreate(title=title, company_id=company_id, gallery=[file_path] if file_path else [])
        created = await crud_project.create_project(db, project_in)
        return created

    except IntegrityError:
        raise HTTPException(status_code=400, detail="Duplicate or invalid fields")
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        print("Error in create_project:", e)
        raise HTTPException(status_code=500, detail="Internal server error")

# ---------------- LIST ----------------
@router.get("/", response_model=List[ProjectRead])
async def get_projects(
    company_id: Optional[int] = Query(None, description="Filter by company ID"),
    db: AsyncSession = Depends(get_db)
):
    """Возвращает список проектов, можно фильтровать по компании."""
    try:
        items = await crud_project.get_projects(db, company_id=company_id)
        return items
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

# ---------------- GET SINGLE ----------------
@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: int = Path(..., gt=0, description="Project ID"),
    db: AsyncSession = Depends(get_db)
):
    """Возвращает один проект по ID."""
    try:
        project = await crud_project.get_project(db, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

# ---------------- UPDATE ----------------
@router.put("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: int = Path(..., gt=0, description="Project ID"),
    title: Optional[str] = Form(None, description="Project title"),
    company_id: Optional[int] = Form(None, description="Company ID"),
    file: UploadFile = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Обновляет проект. Если передан файл, он добавляется в галерею.
    """
    try:
        # Подготавливаем dict для обновления
        updated_data = {}
        if title is not None:
            updated_data["title"] = title
        if company_id is not None:
            updated_data["company_id"] = company_id

        # Работа с галереей
        if file:
            project = await crud_project.get_project(db, project_id)
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")

            file_path = await save_uploaded_file(file, sub_dir="projects")
            updated_data["gallery"] = project.gallery + [file_path]  # добавляем новое изображение к массиву

        updated = await crud_project.update_project(db, project_id, updated_data)
        return updated

    except IntegrityError:
        raise HTTPException(status_code=400, detail="Duplicate or invalid fields")
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        print("Error in update_project:", e)
        raise HTTPException(status_code=500, detail="Internal server error")

# ---------------- DELETE ----------------
@router.delete("/{project_id}", response_model=Message)
async def delete_project(
    project_id: int = Path(..., gt=0, description="Project ID"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Удаляет проект и все файлы галереи."""
    try:
        project = await crud_project.get_project(db, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Удаляем все файлы галереи
        for file_url in project.gallery:
            await delete_uploaded_file(file_url)

        deleted = await crud_project.delete_project(db, project_id)
        return {"success": True, "message": "Project deleted successfully"}

    except IntegrityError:
        raise HTTPException(status_code=400, detail="Could not delete. Dependent records exist")
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        print("Error in delete_project:", e)
        raise HTTPException(status_code=500, detail="Internal server error")
