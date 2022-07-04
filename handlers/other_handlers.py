from aiogram import types
from aiogram.dispatcher.filters import Command

from app import dp
from db.sql_aclhemy import db


@dp.message_handler(Command(['start', 'help'], prefixes='!/'))
async def start(message: types.Message):
    text = """
<b>Привет!</b>
Я создан, чтобы модерировать чаты по Чехии!

Если кто-то нарушает правила, используйте комманду /report на сообщение нарушителя!

Dev: t.me/vsem_azamat
GitHub: github.com/vsem-azamat/moder_bot
    """
    await message.answer(text, disable_web_page_preview=True)
    await message.delete()


@dp.message_handler(Command('chats', prefixes='!/'))
async def get_chats(message: types.Message):
    text = '<b>🎓Образовательные чаты:</b>\n\nПожалуйста, соблюдайте правила!'
    await message.answer(text, reply_markup=db.get_chat_list())
    await message.delete()
