import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config import cnfg
from .models import Base

SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{cnfg.DB_USER}:{cnfg.DB_PASSWORD}@db/{cnfg.DB_NAME}"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False)
sessionmaker = async_sessionmaker(autoflush=True, bind=engine)


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logging.info("Database created")


async def close_db():
    await engine.dispose()
    logging.info("Database closed")
