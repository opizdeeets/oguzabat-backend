from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.models.models import ContactForm
from app.schemas.schemas import ContactFormCreate, ContactFormUpdate
from typing import List, Optional


# CREATE
async def create_contact_form(db: AsyncSession, contact_form_in: ContactFormCreate) -> ContactForm:
    try:
        db_contact_form = ContactForm(**contact_form_in.dict())
        db.add(db_contact_form)
        await db.commit()
        await db.refresh(db_contact_form)
        return db_contact_form
    except IntegrityError:
        await db.rollback()
        raise
    except SQLAlchemyError:
        await db.rollback()
        raise


# READ one
async def get_contact_form(db: AsyncSession, contact_form_id: int) -> Optional[ContactForm]:
    try:
        result = await db.execute(select(ContactForm).where(ContactForm.id == contact_form_id))
        return result.scalars().first()
    except SQLAlchemyError:
        raise


# READ all
async def get_contact_forms(db: AsyncSession) -> List[ContactForm]:
    try:
        result = await db.execute(select(ContactForm))
        return result.scalars().all()
    except SQLAlchemyError:
        raise


# UPDATE
async def update_contact_form(db: AsyncSession, contact_form_id: int, contact_form_in: ContactFormUpdate) -> Optional[ContactForm]:
    try:
        result = await db.execute(select(ContactForm).where(ContactForm.id == contact_form_id))
        db_contact_form = result.scalars().first()

        if not db_contact_form:
            return None

        update_data = contact_form_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_contact_form, field, value)

        await db.commit()
        await db.refresh(db_contact_form)
        return db_contact_form
    except IntegrityError:
        await db.rollback()
        raise
    except SQLAlchemyError:
        await db.rollback()
        raise


# DELETE
async def delete_contact_form(db: AsyncSession, contact_form_id: int) -> bool:
    try:
        result = await db.execute(delete(ContactForm).where(ContactForm.id == contact_form_id))  # Эффективное удаление
        await db.commit()
        return result.rowcount > 0
    except SQLAlchemyError:
        await db.rollback()
        raise