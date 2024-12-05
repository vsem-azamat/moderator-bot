from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, update, select
from sqlalchemy.sql.expression import and_

from database.models import Message


class MessageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_message(
        self,
        chat_id: int,
        user_id: int,
        message_id: int,
        message: str | None,
        message_info: dict,
    ) -> None:
        await self.db.execute(
            insert(Message).values(
                chat_id=chat_id,
                user_id=user_id,
                message_id=message_id,
                message=message,
                message_info=message_info,
            )
        )
        await self.db.commit()

    async def label_spam(self, chat_id: int, message_id: int) -> None:
        query = update(Message).where(and_(Message.chat_id == chat_id, Message.message_id == message_id)).values(spam=True)
        await self.db.execute(query)
        await self.db.commit()

    async def get_user_messages(self, user_id: int) -> Sequence[Message]:
        query = select(Message).where(Message.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalars().all()


def get_message_repository(db: AsyncSession) -> MessageRepository:
    return MessageRepository(db)
