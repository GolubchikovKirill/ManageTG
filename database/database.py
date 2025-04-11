import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import asyncio

load_dotenv()

DB_URL = os.getenv("DB_URL")
engine = create_async_engine(DB_URL, echo=True)
async_session = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)
Base = declarative_base()

async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session

async def create_tables():
    async with engine.begin() as conn:
        # Создаем все таблицы, определенные в моделях
        await conn.run_sync(Base.metadata.create_all)

    print("Таблицы успешно созданы.")


if __name__ == "__main__":
    # Создание таблиц.
    asyncio.run(create_tables())