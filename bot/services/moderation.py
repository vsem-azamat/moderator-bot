import asyncio
from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession
from typing import cast

from bot.logger import logger
from database.repositories import UserRepository, ChatRepository


async def add_to_blacklist(
    db: AsyncSession, 
    bot: Bot, 
    id_tg: int,
    revoke_messages: bool | None = None,
    ) -> None:
    user_repo = UserRepository(db)
    chat_repo = ChatRepository(db)
    await user_repo.add_to_blacklist(id_tg)

    async def ban_user(chat_id: int) -> None:
        try:
            await bot.ban_chat_member(chat_id, id_tg, revoke_messages=revoke_messages)
        except Exception as err:
            logger.warning(
                f"Failed to ban user {id_tg} in chat {chat_id}.\n" f"Maybe the user is already banned.\n" f"Error: {err}"
            )

    tasks = [ban_user(cast(int, chat.id)) for chat in await chat_repo.get_chats()]
    await asyncio.gather(*tasks)
