from aiogram import types
from aiogram.dispatcher.filters import Command

from app import dp
from db.sql_aclhemy import db


@dp.message_handler(Command('chats', prefixes='!/'))
async def get_chats(message: types.Message):
    text = '<b>🎓Образовательные чаты:</b>\n\nПожалуйста, соблюдайте правила!'
    await message.answer(text, reply_markup=db.get_chat_list())
    await message.delete()
