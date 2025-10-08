from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import UploadFile, HTTPException
from typing import List, Optional
import traceback

from app.models.models import Project
from app.schemas.schemas import ProjectCreate, ProjectUpdate
from app.core.uploads import save_uploaded_file, delete_uploaded_file

# ---------------- CREATE ----------------
async def create_project(
    db: AsyncSession,
    project_in: ProjectCreate,
    gallery_files: Optional[List[UploadFile]] = None
) -> Project:
    """
    Создаёт проект с возможной галереей изображений.
    gallery - список ссылок.
    """
    try:
        gallery_urls = []
        if gallery_files:
            if not isinstance(gallery_files, list):
                gallery_files = [gallery_files]
            for f in gallery_files:
                url = await save_uploaded_file(f, sub_dir="project_gallery")
                gallery_urls.append(url)

        db_project = Project(**project_in.dict(), gallery=gallery_urls)
        db.add(db_project)
        await db.commit()
        await db.refresh(db_project)
        return db_project
    except IntegrityError:
        await db.rollback()
        raise
    except SQLAlchemyError:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        print("Error in create_project:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")

# ---------------- READ ONE ----------------
async def get_project(db: AsyncSession, project_id: int) -> Optional[Project]:
    try:
        result = await db.execute(select(Project).where(Project.id == project_id))
        return result.scalars().first()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")

# ---------------- READ ALL ----------------
async def get_projects(db: AsyncSession, company_id: Optional[int] = None) -> List[Project]:
    try:
        stmt = select(Project)
        if company_id:
            stmt = stmt.where(Project.company_id == company_id)
        result = await db.execute(stmt)
        return result.scalars().all()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")

# ---------------- UPDATE ----------------
async def update_project(
    db: AsyncSession,
    project_id: int,
    project_in: ProjectUpdate,
    new_gallery_files: Optional[List[UploadFile]] = None
) -> Optional[Project]:
    try:
        result = await db.execute(select(Project).where(Project.id == project_id))
        db_project = result.scalars().first()
        if not db_project:
            return None

        update_data = project_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_project, field, value)

        if new_gallery_files:
            gallery_urls = db_project.gallery.copy() if db_project.gallery else []
            if not isinstance(new_gallery_files, list):
                new_gallery_files = [new_gallery_files]
            for f in new_gallery_files:
                url = await save_uploaded_file(f, sub_dir="project_gallery")
                gallery_urls.append(url)
            db_project.gallery = gallery_urls

        await db.commit()
        await db.refresh(db_project)
        return db_project
    except IntegrityError:
        await db.rollback()
        raise
    except SQLAlchemyError:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        print("Error in update_project:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")

# ---------------- DELETE ----------------
async def delete_project(db: AsyncSession, project_id: int) -> bool:
    try:
        result = await db.execute(select(Project).where(Project.id == project_id))
        db_project = result.scalars().first()
        if not db_project:
            return False

        if db_project.gallery:
            for url in db_project.gallery:
                await delete_uploaded_file(url)

        await db.delete(db_project)
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        print("Error in delete_project:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")
