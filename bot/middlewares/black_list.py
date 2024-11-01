from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware, Bot, types
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

from database import crud


class BlacklistMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        db: AsyncSession = data["db"]
        blacklisted_users = await crud.get_blocked_users(db)
        blacklisted_ids = {user.id for user in blacklisted_users}
        if isinstance(event, types.Message) and event.from_user.id in blacklisted_ids:
            try:
                await self.bot.ban_chat_member(event.chat.id, event.from_user.id)
                await event.delete()
            except Exception as e:
                print(f"Failed to ban or delete message for user {event.from_user.id}: {e}")
            return  # Stop further handler processing for blacklisted user

        return await handler(event, data)
