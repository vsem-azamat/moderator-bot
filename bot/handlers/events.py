from aiogram import types, Bot, Router

from logger import logger
from bot.utils.filters import ChatTypeFilter


router = Router()


@router.chat_member(
    ChatTypeFilter(["group", "supergroup"]),
    content_types=types.ContentType.NEW_CHAT_MEMBERS,
)
async def welcome_message():
    logger.info("In development")
    pass
