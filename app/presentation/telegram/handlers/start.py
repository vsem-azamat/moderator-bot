from aiogram import types, Router
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from app.presentation.telegram.utils import other
from app.application.services import buttons as buttons_service


router = Router()


@router.message(Command("start", "help", prefix="/!"))
async def start_private(message: types.Message):
    text = (
        "<b>🤖Привет!</b>\n"
        "Я модеририрую чаты по Чехии!\n\n"
        "📚<b>Команды:</b>\n"
        "/chats - список чатов\n"
        "/contacts - контакты\n"
        "/help - помощь\n"
        "/report - пожаловаться (нужно переслать сообщение)\n"
    )
    builder = await buttons_service.get_contacts_buttons()
    bot_message = await message.answer(text, disable_web_page_preview=True, reply_markup=builder.as_markup())
    await message.delete()
    await other.sleep_and_delete(bot_message)


@router.message(Command("chats", prefix="/!"))
async def get_chats(message: types.Message, db: AsyncSession):
    text = "<b>Студенческие чаты:</b>\n\n" "Пожалуйста, соблюдайте правила!\n\n"
    builder = await buttons_service.get_chat_buttons(db)
    bot_message = await message.answer(text, reply_markup=builder.as_markup())
    await message.delete()
    await other.sleep_and_delete(bot_message)


@router.message(Command("contacts", prefix="/!"))
async def get_contacts(message: types.Message):
    text = (
        "📞 <b>Контакты:</b>\n\n"
        "📧 <b>Сотрудничество:</b> @czech_media_admin\n"
        "🧑🏿‍💻 <b>Dev:</b> @vsem_azamat"
    )
    bot_message = await message.answer(text)
    await message.delete()
    await other.sleep_and_delete(bot_message)
