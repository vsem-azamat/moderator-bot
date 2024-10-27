from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware, Bot, types
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

from config import cnfg
from database import crud


class ManagedChatsMiddleware(BaseMiddleware):
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
        if isinstance(event, types.Message) and event.chat.type in ['group', 'supergroup']:
            chat_admins = await self.bot.get_chat_administrators(event.chat.id)
            chat_admins_id = {admin.user.id for admin in chat_admins}
            for super_admin in cnfg.SUPER_ADMINS:
                if super_admin in chat_admins_id:
                    await crud.merge_chat(db, event.chat.id)
                    return await handler(event, data)

            # If at least no one super admin in chat, then leave chat
            await self.bot.leave_chat(event.chat.id)
            return
        return await handler(event, data)