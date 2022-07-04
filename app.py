from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from data import config

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Информация"),

        types.BotCommand("gay", "Радугометр"),
        types.BotCommand("chats", "Образовательные чаты"),
        types.BotCommand("report", "Пожаловаться!")
    ])


async def on_startup(dp):
    import filters
    import throttling

    filters.setup(dp)
    throttling.setup(dp)

    await set_default_commands(dp)

if __name__ == '__main__':
    from aiogram import executor
    from handlers import dp

    executor.start_polling(dp, on_startup=on_startup)
