import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.models.models import User
from app.core.security import hash_password

# 🔧 Прямое подключение — без settings
DATABASE_URL = "postgresql+asyncpg://oguzabat_admin:oguzabat@localhost:5432/oguzabat_db"

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

async def main():
    async with AsyncSessionLocal() as db:
        username = "admin"
        email = "admin@example.com"
        password = "changeme"

        hashed = hash_password(password)
        admin = User(
            username=username,
            email=email,
            hashed_password=hashed,
            is_admin=True
        )
        db.add(admin)
        await db.commit()
        print(f"✅ Админ создан: {username} ({email})")

if __name__ == "__main__":
    asyncio.run(main())
