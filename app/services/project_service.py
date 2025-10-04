from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.models.models import Project, Company
from app.schemas.schemas import ProjectCreate, ProjectUpdate
from typing import List, Optional


# CREATE
async def create_project(db: AsyncSession, project_in: ProjectCreate) -> Project:
    try:
        db_project = Project(**project_in.dict())
        db.add(db_project)
        await db.commit()

        result = await db.execute(
            select(Project)
            .options(selectinload(Project.company))
            .where(Project.id == db_project.id)
        )
        return result.scalar()
    except IntegrityError:
        await db.rollback()
        raise
    except SQLAlchemyError:
        await db.rollback()
        raise


# READ one
async def get_project(db: AsyncSession, project_id: int) -> Optional[Project]:
    try:
        result = await db.execute(
            select(Project)
            .options(selectinload(Project.company))
            .where(Project.id == project_id)
        )
        return result.scalars().first()
    except SQLAlchemyError:
        raise


# READ all (БЕЗ пагинации)
async def get_projects(db: AsyncSession, company_id: Optional[int] = None) -> List[Project]:
    try:
        stmt = select(Project).options(selectinload(Project.company))

        if company_id: 
            stmt = stmt.where(Project.company_id == company_id)

        result = await db.execute(stmt)
        return result.scalars().all()
    except SQLAlchemyError:
        raise


# UPDATE
async def update_project(db: AsyncSession, project_id: int, project_in: ProjectUpdate) -> Optional[Project]:
    try:
        result = await db.execute(select(Project).where(Project.id == project_id))
        db_project = result.scalars().first()

        if not db_project:
            return None

        update_data = project_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_project, field, value)

        await db.commit()

        # Перезагружаем с company для ответа
        result = await db.execute(
            select(Project)
            .options(selectinload(Project.company))
            .where(Project.id == project_id)
        )
        return result.scalar()
    except IntegrityError:
        await db.rollback()
        raise
    except SQLAlchemyError:
        await db.rollback()
        raise


# DELETE
async def delete_project(db: AsyncSession, project_id: int) -> bool:
    try:
        result = await db.execute(delete(Project).where(Project.id == project_id))  # Эффективное удаление
        await db.commit()
        return result.rowcount > 0
    except SQLAlchemyError:
        await db.rollback()
        raise