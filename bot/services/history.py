from aiogram import types

from database.repositories import get_message_repository


async def save_message(db, message: types.Message) -> None:
    chat_id = message.chat.id
    user_id = message.from_user.id
    message_text = message.text
    message_info = message.model_dump()
    
    message_repo = get_message_repository(db)
    await message_repo.add_message(chat_id, user_id, message_text, message_info)
