from sqlalchemy.sql import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config import cnfg
from app.presentation.telegram.logger import logger

SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{cnfg.DB_USER}:{cnfg.DB_PASSWORD}@db/{cnfg.DB_NAME}"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False)
sessionmaker = async_sessionmaker(autoflush=False, bind=engine)


async def close_db():
    await engine.dispose()
    logger.info("Database closed")


async def insert_chat_link():
    sql_script_path = "./scripts/insert_chat_links.sql"  # Corrected file name
    async with engine.begin() as conn:
        with open(sql_script_path, "r") as file:
            for line in file.readlines():
                await conn.execute(text(line))

    logger.info("Chat link inserted")
