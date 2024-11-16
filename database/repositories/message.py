import datetime
from aiogram import types

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update

from database.models import Message


class MessageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_message(
        self,
        chat_id: int,
        user_id: int,
        message: str | None,
        message_info: dict,
    ) -> None:
        await self.db.execute(
            insert(Message).values(
                chat_id=chat_id,
                user_id=user_id,
                message=message,
                message_info=message_info,
            )
        )
        await self.db.commit()


def get_message_repository(db: AsyncSession) -> MessageRepository:
    return MessageRepository(db)
