from random import randint

from aiogram import types
from aiogram.dispatcher.filters import Command

from filters import IsGroup
from loader import dp


@dp.message_handler(IsGroup(), Command("gay", prefixes="!/"))
async def gay_detektor(message: types.Message):
    procent = randint(0, 100)
    text = f"Пользователь 🏳️‍🌈 на {procent}%\n"
    if procent < 50:
        welcome = 'Чел, обдумай еще раз своё поступление в ЧВУТ'
    else:
        welcome = 'Добро пожаловать. Здесь тебе рады.'
    text += welcome
    await message.reply(text)
