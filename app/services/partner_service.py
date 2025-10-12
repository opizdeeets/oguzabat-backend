from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.models.models import Partner
from app.schemas.schemas import PartnerCreate, PartnerUpdate
from app.core.uploads import save_uploaded_file, delete_uploaded_file
from fastapi import UploadFile, HTTPException, status


# ---------------- CREATE ----------------
async def create_partner(
    db: AsyncSession,
    partner_in: PartnerCreate,
    logo_file: UploadFile | None = None
) -> Partner:
    """
    Создаёт партнёра с обработкой загрузки логотипа.
    """

    try:
        # 1️⃣ Сохраняем логотип, если есть
        if logo_file:
            logo_path = await save_uploaded_file(logo_file, sub_dir="partners", max_mb=2)
            partner_in.logo_path = logo_path
        else:
            partner_in.logo_path = ""

        # 2️⃣ Создаём объект SQLAlchemy
        db_partner = Partner(**partner_in.model_dump(exclude_unset=True))

        # 3️⃣ Работа с БД
        db.add(db_partner)
        await db.commit()
        await db.refresh(db_partner)

        return db_partner

    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Ошибка целостности данных: {e}")
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Непредвиденная ошибка: {e}")


# ---------------- READ one ----------------
async def get_partner(db: AsyncSession, partner_id: int) -> Optional[Partner]:
    """
    Возвращает одного партнёра по ID.
    """
    try:
        result = await db.execute(select(Partner).where(Partner.id == partner_id))
        return result.scalars().first()
    except SQLAlchemyError as e:
        raise e


# ---------------- READ all ----------------
async def get_partners(
    db: AsyncSession,
    tags: Optional[List[str]] = None
) -> List[Partner]:
    """
    Возвращает всех партнёров, при необходимости фильтрует по тегам.
    """
    try:
        stmt = select(Partner)
        if tags:
            stmt = stmt.where(Partner.tags.overlap(tags))
        result = await db.execute(stmt)
        return result.scalars().all()
    except SQLAlchemyError as e:
        raise e


# ---------------- UPDATE ----------------
async def update_partner(
    db: AsyncSession,
    partner_id: int,
    partner_in: dict | PartnerUpdate,
    logo: Optional[UploadFile] = None,
    sub_dir: str = "partners"
) -> Partner:
    """
    Обновляет партнёра с возможной заменой логотипа.
    partner_in может быть Pydantic-моделью или словарём.
    """
    # 1️⃣ Получаем сущность из базы
    partner = await db.get(Partner, partner_id)
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Partner с id={partner_id} не найден"
        )

    # 2️⃣ Обработка полей из partner_in
    if isinstance(partner_in, PartnerUpdate):
        update_data = partner_in.model_dump(exclude_unset=True)
    elif isinstance(partner_in, dict):
        update_data = {k: v for k, v in partner_in.items() if v is not None}
    else:
        raise TypeError("partner_in должен быть PartnerUpdate или dict")

    for field, value in update_data.items():
        setattr(partner, field, value)

    # 3️⃣ Обработка нового логотипа
    if logo:
        try:
            # удаляем старый файл
            if partner.logo_path:
                await delete_uploaded_file(partner.logo_path)
            # сохраняем новый
            partner.logo_path = await save_uploaded_file(logo, sub_dir=sub_dir, max_mb=2)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка обработки логотипа: {e}"
            )

    # 4️⃣ Сохраняем изменения в базе
    try:
        db.add(partner)
        await db.commit()
        await db.refresh(partner)
        return partner
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка обновления в базе: {e}"
        )


# ---------------- DELETE ----------------
async def delete_partner(db: AsyncSession, partner_id: int) -> bool:
    """
    Удаляет партнёра и его логотип с диска.
    """
    try:
        result = await db.execute(select(Partner).where(Partner.id == partner_id))
        db_partner = result.scalars().first()
        if not db_partner:
            return False

        if db_partner.logo_path:
            await delete_uploaded_file(db_partner.logo_path)

        await db.delete(db_partner)
        await db.commit()
        return True

    except SQLAlchemyError as e:
        await db.rollback()
        raise e
