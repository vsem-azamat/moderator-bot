from aiogram import types

from database.repositories import get_message_repository, get_user_repository


async def save_message(db, message: types.Message) -> None:
    chat_id = message.chat.id
    user_id = message.from_user.id
    message_id = message.message_id
    message_text = message.text
    message_info = message.model_dump(exclude_none=True)

    message_repo = get_message_repository(db)
    await message_repo.add_message(
        chat_id, 
        user_id,
        message_id, 
        message_text, 
        message_info
    )


async def save_user(db, user: types.User) -> None:
    user_id = user.id
    user_repo = get_user_repository(db)
    await user_repo.add_user_if_is_missing(user_id)
