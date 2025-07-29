from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.repositories import get_message_repository


async def detect_spam(db: AsyncSession, message: types.Message) -> bool:
    text = message.text or message.caption
    if not text:
        return False
    
    message_repo = get_message_repository(db)
    if not await message_repo.is_first_message(
        chat_id=message.chat.id,
        user_id=message.from_user.id
    ):
        return False
    
    if await message_repo.is_similar_spam_message(text):
        return True

    return False
