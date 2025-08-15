from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.repositories import (
    get_chat_repository,
    get_message_repository,
    get_user_repository,
)


async def save_message(db: AsyncSession, message: types.Message) -> None:
    chat_id = message.chat.id
    user_id = message.from_user.id
    message_id = message.message_id
    message_text = message.text or message.caption
    message_info = message.model_dump(exclude_none=True)

    message_repo = get_message_repository(db)
    await message_repo.add_message(chat_id, user_id, message_id, message_text, message_info)


async def merge_user(db: AsyncSession, user: types.User) -> None:
    user_repo = get_user_repository(db)
    await user_repo.merge_user(
        id_tg=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
    )


async def merge_chat(db: AsyncSession, chat: types.Chat) -> None:
    chat_repo = get_chat_repository(db)
    await chat_repo.merge_chat(
        id_tg_chat=chat.id,
        title=chat.title,
        is_forum=chat.is_forum,
    )
