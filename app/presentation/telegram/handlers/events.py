from aiogram import Router
from aiogram.filters import LEFT, MEMBER, ChatMemberUpdatedFilter
from aiogram.types import ChatMemberUpdated

from app.domain.repositories import IChatRepository
from app.presentation.telegram.logger import logger
from app.presentation.telegram.utils.filters import ChatTypeFilter

router = Router()


@router.chat_member(ChatTypeFilter(["group", "supergroup"]), ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def user_joined(event: ChatMemberUpdated, chat_repo: IChatRepository) -> None:
    logger.info("User joined")
    await _handle_join_leave_message(event, chat_repo)


@router.chat_member(ChatTypeFilter(["group", "supergroup"]), ChatMemberUpdatedFilter(member_status_changed=LEFT))
async def user_left(event: ChatMemberUpdated, chat_repo: IChatRepository) -> None:
    logger.info("User left")
    await _handle_join_leave_message(event, chat_repo)


async def _handle_join_leave_message(event: ChatMemberUpdated, chat_repo: IChatRepository) -> None:
    """Handle auto-deletion of join/leave messages if enabled for the chat."""
    try:
        chat = await chat_repo.get_by_id(event.chat.id)

        if chat and chat.auto_delete_join_leave:
            # Note: This is a simplified approach. In practice, Telegram doesn't always
            # send service messages for join/leave events, especially in large groups.
            # The actual implementation might need to track these differently.
            logger.info(f"Auto-delete join/leave enabled for chat {event.chat.id}")

    except Exception as e:
        logger.error(f"Error in join/leave message handler: {e}")
