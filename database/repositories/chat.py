from typing import Sequence
from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Chat


class ChatRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_chat(self, id_tg_chat: int) -> Chat | None:
        result = await self.db.execute(select(Chat).filter(Chat.id == id_tg_chat))
        return result.scalars().first()

    async def get_chats(self) -> Sequence[Chat]:
        result = await self.db.execute(select(Chat))
        return result.scalars().all()

    async def add_if_chat_is_missing(self, id_tg_chat: int) -> None:
        if not await self.get_chat(id_tg_chat):
            await self.db.execute(insert(Chat).values(id=id_tg_chat))
            await self.db.commit()

    async def update_welcome_message(self, id_tg_chat: int, message: str) -> None:
        await self.db.execute(update(Chat).filter(Chat.id == id_tg_chat).values(welcome_message=message))
        await self.db.commit()


def get_chat_repository(db: AsyncSession) -> ChatRepository:
    return ChatRepository(db)
