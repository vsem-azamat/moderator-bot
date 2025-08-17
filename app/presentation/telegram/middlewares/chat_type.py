from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware, types
from aiogram.types import TelegramObject


class ChatTypeMiddleware(BaseMiddleware):
    def __init__(self, chat_types: str | list[str]):
        self.chat_types = chat_types

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, types.Message):
            if isinstance(self.chat_types, str):
                if event.chat.type == self.chat_types:
                    return await handler(event, data)
            elif event.chat.type in self.chat_types:
                return await handler(event, data)
        return None  # Stop further handler processing if chat type does not match
