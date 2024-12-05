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

    async def merge_chat(
        self,
        id_tg_chat: int,
        title: str | None = None,
        is_forum: bool | None = None,
    ) -> None:
        chat = Chat(id=id_tg_chat, title=title, is_forum=is_forum)
        await self.db.merge(chat)
        await self.db.commit()

    async def update_welcome_message(self, id_tg_chat: int, message: str) -> None:
        await self.db.execute(update(Chat).filter(Chat.id == id_tg_chat).values(welcome_message=message))
        await self.db.commit()


def get_chat_repository(db: AsyncSession) -> ChatRepository:
    return ChatRepository(db)
