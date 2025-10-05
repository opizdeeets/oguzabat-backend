from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.models.models import User
from app.schemas.schemas import UserCreate, UserRead
from typing import List, Optional
from app.core.security import hash_password, verify_password

async def create_user(db:AsyncSession,
    username: str,
    email: str,
    password: str,
    is_admin: bool = False) -> User:
    try:
        hashed = hash_password(password)
        db_user = User(username=username, email=email, hashed_password=hashed, is_admin=is_admin)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    except IntegrityError:
        await db.rollback()
        raise
    except SQLAlchemyError:
        await db.rollback()
        raise
                      

async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()

async def get_user(db: AsyncSession, user_id: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()

async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    user = await get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

async def update_user(db: AsyncSession, user_id: int, **fields) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    db_user = result.scalars().first()
    if not db_user:
        return None
    # Prevent clients from updating created_at
    fields.pop("created_at", None)
    for k, v in fields.items():
        setattr(db_user, k, v)
    await db.commit()
    await db.refresh(db_user)
    return db_user    

async def delete_user(db: AsyncSession, user_id: int) -> bool:
    result = await db.execute(select(User).where(User.id == user_id))
    db_user = result.scalars().first()
    if not db_user:
        return False
    await db.delete(db_user)
    await db.commit()
    return True
