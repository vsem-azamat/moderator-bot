from aiogram import types
from aiogram.types.message import ParseMode
from aiogram.utils.markdown import hlink

from aiogram.types import InputFile
from aiogram.dispatcher.filters import Command

from loader import dp, bot
from filters import SuperAdmins

import defs


@dp.message_handler(Command('test', prefixes='!/'), SuperAdmins())
async def test(message: types.Message):
    await message.reply('test')


@dp.message_handler(Command('json'))
async def json(message: types.Message):
    await message.reply(message)
    