import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

from config import cnfg
from app.presentation.telegram.logger import logger
from app.presentation.telegram.handlers import router
from app.presentation.telegram.middlewares import (
    HistoryMiddleware,
    DependenciesMiddleware,
    BlacklistMiddleware,
    ManagedChatsMiddleware,
)
from app.infrastructure.db.session import sessionmaker, close_db, insert_chat_link


async def on_startup(bot: Bot) -> None:
    await bot.delete_webhook()
    logger.info("Bot started")
    await insert_chat_link()


async def on_shutdown(bot: Bot) -> None:
    await bot.delete_webhook()
    await bot.close()
    await close_db()
    logger.info("Bot stopped")


async def get_bot_and_dp() -> tuple[Bot, Dispatcher]:
    bot = Bot(token=cnfg.BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()
    return bot, dp


async def main() -> None:
    bot, dp = await get_bot_and_dp()
    dp.update.middleware(DependenciesMiddleware(session_pool=sessionmaker, bot=bot))
    dp.update.middleware(ManagedChatsMiddleware())
    dp.update.middleware(HistoryMiddleware())
    dp.message.middleware(BlacklistMiddleware())
    dp.callback_query.middleware(CallbackAnswerMiddleware())

    try:
        dp.include_router(router)
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        await dp.start_polling(bot, skip_updates=True)

    except Exception as e:
        logger.info(e)

    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
