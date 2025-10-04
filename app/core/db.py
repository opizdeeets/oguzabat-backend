from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql+asyncpg://oguzabat_admin:oguzabat@localhost:5432/oguzabat_db"

engine = create_async_engine(DATABASE_URL, echo = True)

AsyncSessionLocal = sessionmaker(
    bind = engine,
    class_= AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session