from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.models.models import ContactForm
from app.schemas.schemas import ContactFormCreate, ContactFormUpdate
from fastapi import HTTPException, status
from typing import List, Optional


# ---------------- CREATE ----------------
async def create_contact_form(
    db: AsyncSession,
    contact_form_in: ContactFormCreate,
    map_code: str | None = None
) -> ContactForm:
    """
    Создает запись ContactForm.
    map_code можно передать отдельно.
    Пробрасывает исключения, чтобы роутер решал как их обрабатывать.
    """
    db_contact_form = ContactForm(**contact_form_in.model_dump())

    if map_code:
        db_contact_form.map_code = map_code

    db.add(db_contact_form)
    try:
        await db.commit()
        await db.refresh(db_contact_form)
    except IntegrityError:
        await db.rollback()
        raise
    except SQLAlchemyError:
        await db.rollback()
        raise
    return db_contact_form


# ---------------- READ ONE ----------------
async def get_contact_form(db: AsyncSession, contact_form_id: int) -> Optional[ContactForm]:
    """
    Получение одной формы по ID.
    Пробрасывает исключения, не оборачивает в HTTPException.
    """
    result = await db.execute(select(ContactForm).where(ContactForm.id == contact_form_id))
    contact = result.scalars().first()
    if not contact:
        # Сервис возвращает None, чтобы роутер мог сам решать HTTP код
        return None
    return contact


# ---------------- READ ALL ----------------
async def get_contact_forms(db: AsyncSession) -> List[ContactForm]:
    """
    Возвращает список всех форм.
    """
    result = await db.execute(select(ContactForm))
    return result.scalars().all()


# ---------------- UPDATE ----------------
async def update_contact_form(
    db: AsyncSession,
    contact_form_id: int,
    contact_form_in: ContactFormUpdate,
    map_code: Optional[str] = None
) -> Optional[ContactForm]:
    """
    Обновляет форму контакта.
    map_code можно передать отдельно.
    Возвращает None если запись не найдена.
    """
    result = await db.execute(select(ContactForm).where(ContactForm.id == contact_form_id))
    db_contact_form = result.scalars().first()
    if not db_contact_form:
        return None

    update_data = contact_form_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_contact_form, field, value)

    if map_code is not None:
        db_contact_form.map_code = map_code

    try:
        await db.commit()
        await db.refresh(db_contact_form)
    except IntegrityError:
        await db.rollback()
        raise
    except SQLAlchemyError:
        await db.rollback()
        raise

    return db_contact_form


# ---------------- DELETE ----------------
async def delete_contact_form(db: AsyncSession, contact_form_id: int) -> bool:
    """
    Удаляет форму контакта.
    Возвращает True если удалено хотя бы одно значение.
    """
    try:
        result = await db.execute(delete(ContactForm).where(ContactForm.id == contact_form_id))
        await db.commit()
        return result.rowcount > 0
    except SQLAlchemyError:
        await db.rollback()
        raise