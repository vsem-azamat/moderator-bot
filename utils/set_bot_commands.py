from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Запустить бота"),
        types.BotCommand("help", "Помощь"),

        # types.BotCommand("ban", "Забанить"),
        # types.BotCommand("unban", "Разбанить"),

        types.BotCommand("mute", "Заблокировать"),
        types.BotCommand("unmute", "Разблокировать"),


        # types.BotCommand("ro", "Режим Read Only"),
        # types.BotCommand("unro", "Отключить RO"),
    ])
    pass
