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
    test = await message.reply('test')
    print(test)
