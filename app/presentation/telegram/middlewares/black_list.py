from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware, Bot, types
from aiogram.types import TelegramObject

from app.presentation.telegram.logger import logger
from app.infrastructure.db.repositories import UserRepository


class BlacklistMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        bot: Bot = data["bot"]
        user_repo: UserRepository = data["user_repo"]
        blacklisted_users = await user_repo.get_blocked_users()
        blacklisted_ids = {user.id for user in blacklisted_users}
        if isinstance(event, types.Message) and event.from_user.id in blacklisted_ids:
            try:
                await bot.ban_chat_member(event.chat.id, event.from_user.id)
                await event.delete()
            except Exception as e:
                logger.error(f"Failed to ban or delete message for user {event.from_user.id}: {e}")
            return  # Stop further handler processing for blacklisted user

        return await handler(event, data)
