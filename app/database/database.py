import asyncio
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.settings import DB_URL


engine = create_async_engine(DB_URL, echo=True)


class Base(DeclarativeBase):
    pass


async_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)


# Используем как Depends(get_db)
async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session


# Используем для создания таблиц
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Таблицы успешно созданы.")


# CLI-запуск
if __name__ == "__main__":
    asyncio.run(create_tables())
