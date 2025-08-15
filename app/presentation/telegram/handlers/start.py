from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services import buttons as buttons_service
from app.core.config import settings
from app.infrastructure.db.repositories import AdminRepository
from app.presentation.telegram.utils import other

router = Router()


@router.message(Command("start", "help", prefix="/!"))
async def start_private(message: types.Message, admin_repo: AdminRepository):
    text = (
        "<b>🤖 Привет!</b>\n"
        "Я модерирую чаты по Чехии!\n\n"
        "📚 <b>Команды:</b>\n"
        "• /chats - список чатов\n"
        "• /contacts - контакты\n"
        "• /help - помощь\n"
        "• /report - пожаловаться (нужно переслать сообщение)\n"
    )

    is_admin = message.from_user.id in settings.admin.super_admins or await admin_repo.is_admin(message.from_user.id)
    if is_admin:
        text += (
            "\n\n<b>👮 Команды для админов:</b>\n"
            "• /mute - замутить пользователя\n"
            "• /unmute - размутить пользователя\n"
            "• /ban - бан и добавить в ЧС\n"
            "• /unban - убрать из ЧС\n"
            "• /black - занести в ЧС всех чатов\n"
            "• /blacklist - посмотреть ЧС\n"
            "• /welcome &lt;text&gt; - изменить приветствие\n"
            "• /admin - добавить админа (ответом)\n"
            "• /unadmin - убрать админа (ответом)\n"
            "• /json - получить JSON сообщения\n"
        )

    builder = await buttons_service.get_contacts_buttons()
    bot_message = await message.answer(
        text,
        disable_web_page_preview=True,
        reply_markup=builder.as_markup(),
    )
    await message.delete()
    await other.sleep_and_delete(bot_message)


@router.message(Command("chats", prefix="/!"))
async def get_chats(message: types.Message, db: AsyncSession):
    text = "<b>Студенческие чаты:</b>\n\nПожалуйста, соблюдайте правила!\n\n"
    builder = await buttons_service.get_chat_buttons(db)
    bot_message = await message.answer(text, reply_markup=builder.as_markup())
    await message.delete()
    await other.sleep_and_delete(bot_message)


@router.message(Command("contacts", prefix="/!"))
async def get_contacts(message: types.Message):
    text = "📞 <b>Контакты:</b>\n\n• 📧 <b>Сотрудничество:</b> @czech_media_admin\n• 🧑🏿‍💻 <b>Dev:</b> @vsem_azamat"
    bot_message = await message.answer(text)
    await message.delete()
    await other.sleep_and_delete(bot_message)
