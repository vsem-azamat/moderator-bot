from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware, types
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

from logger import logger
from bot.services import history as history_service


class HistoryMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        db: AsyncSession = data["db"]
        if isinstance(event, types.Message):
            try:
                await history_service.save_message(db, event)
            except Exception as err:
                logger.error(f"Error while saving message: {err}")

        return await handler(event, data)
