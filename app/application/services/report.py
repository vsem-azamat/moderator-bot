from aiogram import Bot, types

from app.core.config import settings
from app.presentation.telegram.utils import other


async def report_to_moderators(
    bot: Bot, reporter: types.User, reported: types.User, reported_message: types.Message
) -> None:
    chat_mention = await other.get_chat_mention(reported_message)
    reported_message_metion = await other.get_message_mention(reported_message)

    text = (
        f"🚨 <b>От:</b> {await other.get_user_mention(reporter)}\n"
        f"🎯 <b>На:</b> {await other.get_user_mention(reported)}\n"
        f"💬 <b>Чат:</b> {chat_mention}\n\n"
        f"📝 {reported_message_metion}:\n"
        f"{reported_message.text}"
    )
    await bot.send_message(chat_id=settings.admin.default_report_chat_id, text=text)
