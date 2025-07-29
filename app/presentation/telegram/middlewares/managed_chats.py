from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware, Bot, types
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

from config import cnfg
from app.application.services import history as history_service


class ManagedChatsMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        bot: Bot = data["bot"]
        db: AsyncSession = data["db"]
        if (
            isinstance(event, types.Update) 
            and isinstance(event.message, types.Message)
            and event.message.chat.type in ["group", "supergroup"]
        ):
            message = event.message
            chat_admins = await bot.get_chat_administrators(message.chat.id)
            chat_admins_id = {admin.user.id for admin in chat_admins}
            if any(super_admin in chat_admins_id for super_admin in cnfg.SUPER_ADMINS):
                await history_service.merge_chat(db, message.chat)
                return await handler(event, data)

            # If at least no one super admin in chat, then leave chat
            await bot.leave_chat(message.chat.id)
            return
        return await handler(event, data)
