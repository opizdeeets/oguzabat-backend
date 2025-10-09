from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from typing import List
from datetime import datetime

from app.models.models import Project
from app.schemas.schemas import ProjectCreate, ProjectUpdate


async def create_project(db: AsyncSession, project_in: ProjectCreate, gallery_files: List[str]) -> Project:
    try:
        # Если клиент не передал дату, ставим текущую UTC без tzinfo
        opened_date = project_in.opened_date or datetime.utcnow()
        if opened_date.tzinfo is not None:
            opened_date = opened_date.replace(tzinfo=None)

        db_project = Project(
            company_id=project_in.company_id,
            name=project_in.name,
            type=project_in.type,
            location=project_in.location,
            opened_date=opened_date,
            status=project_in.status,
            short_description=project_in.short_description,
            full_description=project_in.full_description,
            gallery=gallery_files or []
        )
        db.add(db_project)
        await db.commit()
        await db.refresh(db_project)
        return db_project
    except SQLAlchemyError as e:
        await db.rollback()
        raise e


async def update_project(db: AsyncSession, project: Project, project_in: ProjectUpdate, gallery_files: List[str] = None) -> Project:
    try:
        # Обновляем поля по мере необходимости
        for field, value in project_in.dict(exclude_unset=True).items():
            if field == "opened_date" and value:
                if value.tzinfo is not None:
                    value = value.replace(tzinfo=None)
            setattr(project, field, value)

        if gallery_files is not None:
            project.gallery = gallery_files

        await db.commit()
        await db.refresh(project)
        return project
    except SQLAlchemyError as e:
        await db.rollback()
        raise e


async def get_project(db: AsyncSession, project_id: int) -> Project | None:
    result = await db.get(Project, project_id)
    return result


async def delete_project(db: AsyncSession, project: Project):
    try:
        await db.delete(project)
        await db.commit()
    except SQLAlchemyError as e:
        await db.rollback()
        raise e
