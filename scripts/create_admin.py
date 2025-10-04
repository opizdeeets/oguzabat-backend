import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from app.core.config import settings
from app.core.db import Base 
from app.models.models import User
from app.core.security import hash_password

DATABASE_URL = "postgresql+asyncpg://oguzabat_admin:oguzabat@localhost:5432/oguzabat_db"

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

async def main():
    async with AsyncSessionLocal() as db:
        username = "admin"
        email = "admin@example.com"
        password = "changeme"
        hashed = hash_password(password)
        user = User(username=username, email=email, hashed_password=hashed, is_admin=True)
        db.add(user)
        await db.commit()
        print("Admin created:", username)

if __name__ == "__main__":
    asyncio.run(main())        