import time
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any

from aiogram import BaseMiddleware, Bot, types
from aiogram.types import TelegramObject

from app.application.services import history as history_service
from app.core.config import settings

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class ManagedChatsMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        super().__init__()
        self._admin_cache: dict[int, tuple[set[int], float]] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        bot: Bot = data["bot"]
        db: AsyncSession = data["db"]
        if (
            isinstance(event, types.Update)
            and isinstance(event.message, types.Message)
            and event.message.chat.type in ["group", "supergroup"]
        ):
            message = event.message
            chat_admins_id = await self._get_cached_chat_admins(bot, message.chat.id)
            if any(super_admin in chat_admins_id for super_admin in settings.admin.super_admins):
                await history_service.merge_chat(db, message.chat)
                return await handler(event, data)

            # If at least no one super admin in chat, then leave chat
            await bot.leave_chat(message.chat.id)
            return None
        return await handler(event, data)

    async def _get_cached_chat_admins(self, bot: Bot, chat_id: int) -> set[int]:
        """Get chat admins with caching (TTL=30 minutes)."""
        current_time = time.time()

        # Check if we have cached data and it's not expired
        if chat_id in self._admin_cache:
            admins_set, timestamp = self._admin_cache[chat_id]
            if current_time - timestamp < 1800:  # 30 minutes = 1800 seconds
                return admins_set

        # Cache expired or not exists, fetch new data
        chat_admins = await bot.get_chat_administrators(chat_id)
        admins_set = {admin.user.id for admin in chat_admins}

        # Cache the result
        self._admin_cache[chat_id] = (admins_set, current_time)

        return admins_set
