from aiogram import types
from aiogram.types.message import ParseMode
from aiogram.utils.markdown import hlink

from aiogram.types import InputFile
from aiogram.dispatcher.filters import Command

from app import dp, bot
from filters import SuperAdmins
from db.sql_aclhemy import db


@dp.message_handler(Command('test', prefixes='!/'), SuperAdmins())
async def test(message: types.Message):
    text = f"<a href='{message.url}'>LINK</a>"
    await message.answer(message.url)


@dp.message_handler(Command('json'), SuperAdmins())
async def json(message: types.Message):
    await message.reply(message)
    