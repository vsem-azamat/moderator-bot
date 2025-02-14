import asyncio
from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession
from typing import cast

from bot.logger import logger
from database.repositories import UserRepository, ChatRepository, MessageRepository


async def add_to_blacklist(
    db: AsyncSession, 
    bot: Bot, 
    id_tg: int,
    revoke_messages: bool | None = None,
    ) -> None:
    user_repo = UserRepository(db)
    chat_repo = ChatRepository(db)
    message_repo = MessageRepository(db)
    await user_repo.add_to_blacklist(id_tg)

    async def ban_user(chat_id: int) -> None:
        try:
            member = await bot.get_chat_member(chat_id, id_tg)
            if member.status not in ['left', 'kicked']:
                await bot.ban_chat_member(chat_id, id_tg, revoke_messages=revoke_messages)
            else:
                user_messages = await message_repo.get_user_messages(id_tg)
                for message in user_messages:
                    await message_repo.label_spam(
                        chat_id=cast(int, message.chat_id),
                        message_id=cast(int, message.message_id),
                    )
        except Exception as err:
            logger.warning(
                f"Failed to ban user {id_tg} in chat {chat_id}.\n" f"Maybe the user is already banned or not in the chat.\n" f"Error: {err}"
            )

    tasks = [ban_user(cast(int, chat.id)) for chat in await chat_repo.get_chats()]
    await asyncio.gather(*tasks)
