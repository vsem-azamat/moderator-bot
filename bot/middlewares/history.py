from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware, types
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

from bot.logger import logger
from bot.utils import other
from bot.services import history as history_service, spam as spam_service


class HistoryMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        db: AsyncSession = data["db"]
        if isinstance(event, types.Update) and isinstance(event.message, types.Message):
            message = event.message
            user = message.from_user

            if isinstance(user, types.User):
                try:
                    await history_service.merge_user(db, user)
                except Exception as err:
                    logger.error(f"Error while saving user: {err}")

            try:
                await history_service.save_message(db, message)
            except Exception as err:
                logger.error(f"Error while saving message: {err}")

            if await spam_service.detect_spam(db, message):
                answer = await event.message.answer("🚧 Is spam message?🤔")
                await other.sleep_and_delete(answer, 15)

        return await handler(event, data)
