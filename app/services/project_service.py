from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import UploadFile, HTTPException
from typing import List, Optional

from app.models.models import Project, ProjectGallery, Company
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
    """
    try:
        gallery_objs = []
        if gallery_files:
            if not isinstance(gallery_files, list):
                gallery_files = [gallery_files]
            for f in gallery_files:
                url = await save_uploaded_file(f, sub_dir="project_gallery")
                gallery_objs.append(ProjectGallery(file_url=url))

        db_project = Project(**project_in.dict(), gallery=gallery_objs)
        db.add(db_project)
        await db.commit()

        result = await db.execute(
            select(Project)
            .options(selectinload(Project.company), selectinload(Project.gallery))
            .where(Project.id == db_project.id)
        )
        return result.scalars().first()
    except IntegrityError:
        await db.rollback()
        raise
    except SQLAlchemyError:
        await db.rollback()
        raise

# ---------------- READ ONE ----------------
async def get_project(db: AsyncSession, project_id: int) -> Optional[Project]:
    try:
        result = await db.execute(
            select(Project)
            .options(selectinload(Project.company), selectinload(Project.gallery))
            .where(Project.id == project_id)
        )
        return result.scalars().first()
    except SQLAlchemyError:
        raise

# ---------------- READ ALL ----------------
async def get_projects(db: AsyncSession, company_id: Optional[int] = None) -> List[Project]:
    try:
        stmt = select(Project).options(selectinload(Project.company), selectinload(Project.gallery))
        if company_id:
            stmt = stmt.where(Project.company_id == company_id)
        result = await db.execute(stmt)
        return result.scalars().all()
    except SQLAlchemyError:
        raise

# ---------------- UPDATE ----------------
async def update_project(
    db: AsyncSession,
    project_id: int,
    project_in: ProjectUpdate,
    new_gallery_files: Optional[List[UploadFile]] = None
) -> Optional[Project]:
    result = await db.execute(select(Project).where(Project.id == project_id).options(selectinload(Project.gallery)))
    db_project = result.scalars().first()
    if not db_project:
        return None

    update_data = project_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_project, field, value)

    # Добавляем новые файлы в галерею
    if new_gallery_files:
        if not isinstance(new_gallery_files, list):
            new_gallery_files = [new_gallery_files]
        for f in new_gallery_files:
            url = await save_uploaded_file(f, sub_dir="project_gallery")
            db_project.gallery.append(ProjectGallery(file_url=url))

    await db.commit()

    # Перезагружаем объект с company и gallery
    result = await db.execute(
        select(Project)
        .options(selectinload(Project.company), selectinload(Project.gallery))
        .where(Project.id == project_id)
    )
    return result.scalars().first()

# ---------------- DELETE ----------------
async def delete_project(db: AsyncSession, project_id: int) -> bool:
    result = await db.execute(
        select(Project).where(Project.id == project_id).options(selectinload(Project.gallery))
    )
    db_project = result.scalars().first()
    if not db_project:
        return False

    # Удаляем файлы галереи
    for f in db_project.gallery:
        await delete_uploaded_file(f.file_url)

    await db.delete(db_project)
    await db.commit()
    return True
