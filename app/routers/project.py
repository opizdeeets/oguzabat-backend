from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import List, Optional

from app.core.db import get_db
from app.core.deps import get_current_admin_user
from app.models.models import Project
from app.schemas.schemas import ProjectCreate, ProjectUpdate, ProjectRead, Message
from app.services import project_service as crud_project


router = APIRouter(
    prefix="/projects",
    tags=["projects"]
)


@router.post("/", response_model=ProjectRead, status_code= status.HTTP_201_CREATED)
async def create_project(
    project_in: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(get_current_admin_user)
):
    """
    Create a new project
    """
    try:
        created = await crud_project.create_project(db, project_in)
        return created
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not create project. Possibly duplicate or invalid fields.")
    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    
@router.get("/", 
    response_model=List[ProjectRead],
    responses={
        500: {"model": Message, "description": "Internal server error"}
    }
)
async def get_projects(
    company_id: Optional[int] = Query(None, description="Filter by company ID"),
    db: AsyncSession = Depends(get_db)
): 
    try:
        items = await crud_project.get_projects(db, company_id=company_id)
        return items
    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/{project_id}", 
    response_model=ProjectRead,
    responses={
        404: {"model": Message, "description": "Project not found"},
        500: {"model": Message, "description": "Internal server error"}
    }
)
async def get_project(
    project_id: int = Path(..., gt=0, example=1, description="Project ID"),
    db: AsyncSession = Depends(get_db)
):
    try:
        project = await crud_project.get_project(db, project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        return project
    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.put("/{project_id}", 
    response_model=ProjectRead,
    responses={
        404: {"model": Message, "description": "Project not found"},
        400: {"model": Message, "description": "Duplicate or invalid data"}, 
        500: {"model": Message, "description": "Internal server error"}
    }
)
async def update_project(
    project_id: int = Path(..., gt=0, example=1, description="Project ID"),  # ✅ ПЕРВЫЙ ПАРАМЕТР
    project_in: ProjectUpdate = Body(..., description="Project data to update"),                                         # ✅ ПОТОМ BODY
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(get_current_admin_user)
):
    try:
        updated = await crud_project.update_project(db, project_id, project_in.dict(exclude_unset=True))
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        return updated
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not update project. Possibly duplicate or invalid fields.")
    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.delete("/{project_id}", response_model=Message)
async def delete_project(
    project_id: int = Path(..., gt=0, example=1, description="Project ID"),
    db: AsyncSession = Depends(get_db),
    admin_user: dict = Depends(get_current_admin_user)
):
    try:
        deleted = await crud_project.delete_project(db, project_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        return {"success": True, "message": "Project deleted successfully."}
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not delete project. Possibly dependent records exist.")
    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")