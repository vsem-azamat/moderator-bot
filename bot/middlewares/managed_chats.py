from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware, Bot, types
from aiogram.types import TelegramObject

from config import cnfg
from bot.services import history as history_service
from database.repositories import ChatRepository


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
        chat_repo: ChatRepository = data["chat_repo"]
        if isinstance(event, types.Message) and event.chat.type in [
            "group",
            "supergroup",
        ]:
            chat_admins = await bot.get_chat_administrators(event.chat.id)
            chat_admins_id = {admin.user.id for admin in chat_admins}
            for super_admin in cnfg.SUPER_ADMINS:
                if super_admin in chat_admins_id:
                    await history_service.merge_chat(chat_repo, event.chat)
                    return await handler(event, data)

            # If at least no one super admin in chat, then leave chat
            await bot.leave_chat(event.chat.id)
            return
        return await handler(event, data)
