from aiogram import types
from aiogram.dispatcher.filters import Command
from filters import Memes
from app import dp, bot

from random import randint
import datetime


list_commands = ["/meme"]

@dp.message_handler(Command("gay", prefixes="!/"), Memes())
async def gay_detektor(message: types.Message):
    pr = randint(0, 100)
    user_href = f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>"
    text = f"{user_href} 🏳️‍🌈 на {pr}%\n"
    if 90 <= pr:
        welcome = 'гОтОвь свОЁ ОчкО тОвАрИщЬ!!!'
    elif pr == 69:
        welcome = 'Уже пишу твоей Маме, чел'
    elif 50 < pr < 90:
        welcome = 'Добро пожаловать. Здесь тебе рады.'
    elif 10 < pr <= 50:
        welcome = 'Чел, обдумай еще раз своё поступление в ЧВУТ...'
    else:
        welcome = 'СКАТЕРТЬЮ ДОРОЖКА В ЧЗУ, НАТУРАЛ!!!\nИ ЛОВИ МУТ, ПОЗЕР'
        ReadOnlyPremissions = types.ChatPermissions(
            can_send_messages=False,
            can_send_media_messages=False,
            can_send_polls=False,
            can_send_other_messages=False
        )
        try:
            mute_date = datetime.datetime.now() + datetime.timedelta(minutes=3)
            await bot.restrict_chat_member(message.chat.id, message.from_user.id, ReadOnlyPremissions, mute_date)
        except:
            pass
    text += welcome

    await message.answer(text)
    await message.delete()
