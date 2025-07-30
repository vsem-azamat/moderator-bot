from aiogram import types, Bot, Router

from app.presentation.telegram.logger import logger
from app.presentation.telegram.utils.filters import ChatTypeFilter


router = Router()


@router.chat_member(
    ChatTypeFilter(["group", "supergroup"]),
    content_types=types.ContentType.NEW_CHAT_MEMBERS,
)
async def welcome_message():
    logger.info("In development")
    pass
