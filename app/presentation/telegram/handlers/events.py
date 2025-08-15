from aiogram import Router
from aiogram.filters import LEFT, MEMBER, ChatMemberUpdatedFilter
from aiogram.types import ChatMemberUpdated

from app.presentation.telegram.logger import logger
from app.presentation.telegram.utils.filters import ChatTypeFilter

router = Router()


@router.chat_member(ChatTypeFilter(["group", "supergroup"]), ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def user_joined(_event: ChatMemberUpdated):
    logger.info("User joined")


@router.chat_member(ChatTypeFilter(["group", "supergroup"]), ChatMemberUpdatedFilter(member_status_changed=LEFT))
async def user_left(_event: ChatMemberUpdated):
    logger.info("User left")
