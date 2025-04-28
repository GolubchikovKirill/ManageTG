import asyncio
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.config import settings


engine = create_async_engine(settings.db_url, echo=True)


class Base(DeclarativeBase):
    pass


async_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)



async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session


async def reset_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        print("Таблицы успешно удалены.")

        await conn.run_sync(Base.metadata.create_all)
        print("Таблицы успешно созданы.")


# CLI-запуск
if __name__ == "__main__":
    asyncio.run(reset_tables())