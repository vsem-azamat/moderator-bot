from aiogram import types, Router, Bot
from aiogram.filters import Command

from app.presentation.telegram.utils import other
from app.application.services import report as report_services


router = Router()


@router.message(Command("report", prefix="!/"))
async def report_user(message: types.Message, bot: Bot):
    if not message.reply_to_message:
        answer = await message.answer("Эту команду нужно использовать в ответ на сообщение.")
        await other.sleep_and_delete(answer, 10)

    elif not message.reply_to_message.from_user:
        answer = await message.answer("Это не пользователь.")
        await other.sleep_and_delete(answer, 10)

    else:
        reporter = message.from_user
        reported = message.reply_to_message.from_user
        reported_message = message.reply_to_message
        await report_services.report_to_moderators(bot, reporter, reported, reported_message)
        answer = await message.answer("Спасибо! Модераторы оповещены.👮")

    await message.delete()
