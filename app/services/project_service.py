# app/services/project_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import Project
from app.core.uploads import save_uploaded_file, delete_uploaded_file
from app.schemas.schemas import ProjectCreate, ProjectUpdate
from typing import List, Optional


# ---------- CREATE ----------
async def create_project(
    db: AsyncSession,
    project_in: ProjectCreate,
    gallery_files: Optional[List[str]] = None
) -> Project:
    """
    Создаёт новый проект. Дата и время устанавливаются автоматически (server_default).
    """
    project = Project(
        **project_in.dict(),
        gallery=gallery_files or []  # предотвращает ошибку NoneType
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


# ---------- READ ----------
async def get_projects(
    db: AsyncSession,
    company_id: Optional[int] = None
) -> List[Project]:
    """
    Возвращает список всех проектов, опционально фильтруя по компании.
    """
    query = select(Project)
    if company_id:
        query = query.filter(Project.company_id == company_id)

    result = await db.execute(query)
    return result.scalars().all()


async def get_project(
    db: AsyncSession,
    project_id: int
) -> Optional[Project]:
    """
    Возвращает проект по ID.
    """
    result = await db.execute(select(Project).filter(Project.id == project_id))
    return result.scalars().first()


# ---------- UPDATE ----------
async def update_project(
    db: AsyncSession,
    project_id: int,
    project_in: ProjectUpdate,
    new_gallery_files: Optional[List[str]] = None
) -> Optional[Project]:
    """
    Обновляет данные проекта. Если переданы новые файлы — заменяет галерею.
    """
    project = await get_project(db, project_id)
    if not project:
        return None

    update_data = project_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)

    if new_gallery_files is not None:
        # безопасное удаление старых файлов
        for old_path in project.gallery or []:
            await delete_uploaded_file(old_path)
        project.gallery = new_gallery_files

    await db.commit()
    await db.refresh(project)
    return project


# ---------- DELETE ----------
async def delete_project(
    db: AsyncSession,
    project_id: int
) -> bool:
    """
    Удаляет проект и связанные файлы галереи.
    """
    project = await get_project(db, project_id)
    if not project:
        return False

    # удаляем все файлы галереи
    for path in project.gallery or []:
        await delete_uploaded_file(path)

    await db.delete(project)
    await db.commit()
    return True
