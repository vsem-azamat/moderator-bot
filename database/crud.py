from typing import Sequence
from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Admin, User, Chat, ChatLink


async def get_user(db: AsyncSession, id_tg: int) -> User | None:
    result = await db.execute(select(User).filter(User.id == id_tg))
    return result.scalars().first()


async def get_blocked_users(db: AsyncSession) -> Sequence[User]:
    result = await db.execute(select(User).filter(User.blocked == True))
    return result.scalars().all()


async def get_chat(db: AsyncSession, id_tg_chat: int) -> Chat | None:
    result = await db.execute(select(Chat).filter(Chat.id == id_tg_chat))
    return result.scalars().first()


async def get_chats(db: AsyncSession) -> Sequence[Chat]:
    result = await db.execute(select(Chat))
    return result.scalars().all()


async def get_chat_links(db: AsyncSession) -> Sequence[ChatLink]:
    result = await db.execute(select(ChatLink).order_by(ChatLink.priority.desc()))
    return result.scalars().all()


async def get_db_admins(db: AsyncSession) -> Sequence[Admin]:
    result = await db.execute(select(Admin))
    return result.scalars().all()


async def merge_chat(db: AsyncSession, id_tg_chat: int) -> None:
    if not await get_chat(db, id_tg_chat):
        await db.execute(insert(Chat).values(id=id_tg_chat))
        await db.commit()


async def update_welcome_message(db: AsyncSession, id_tg_chat: int, message: str) -> None:
    await db.execute(update(Chat).filter(Chat.id == id_tg_chat).values(welcome_message=message))
    await db.commit()


async def insert_admin(db: AsyncSession, id_tg: int) -> None:
    await db.execute(insert(Admin).values(id=id_tg))
    await db.commit()


async def add_blacklist(db: AsyncSession, id_tg: int) -> None:
    await db.execute(insert(User).values(id=id_tg, blocked=True))
    await db.commit()
