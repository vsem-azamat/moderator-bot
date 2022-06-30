import asyncio
import datetime
import re
from db.sql_aclhemy import db
from defs import get_mention

from aiogram import exceptions
from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.utils.exceptions import BadRequest

from filters import IsGroup, AdminFilter
from loader import dp, bot


# MUTE and UNMUTE
@dp.message_handler(IsGroup(), Command("mute", prefixes='!/'), AdminFilter())
async def mute_member(message: types.Message):
    mute_date = db.mute_date(message.from_user.id, message.chat.id, message.text)

    ReadOnlyPremissions = types.ChatPermissions(
        can_send_messages=False,
        can_send_media_messages=False,
        can_send_polls=False,
        can_send_other_messages=False
    )

    try:
        await bot.restrict_chat_member(chat_id=message.chat.id, user_id=message.from_user.id, permissions=ReadOnlyPremissions,
                                       until_date=mute_date['until_date'])        
        time = mute_date.get('time')
        unit = mute_date.get('unit','m')
        until_date = mute_date['until_date'].strftime("%Y-%m-%d %H:%M:%S")
        
        mute_text = f"Пользователь {get_mention(message)} в муте на {time} {unit}.\nДата размута: {until_date}"
        await message.reply(mute_text)

    except AttributeError: 
        await message.answer("Примените команду к сообщение челока, которого нужно замутить.")

    except exceptions.CantRestrictChatOwner:
        await message.answer("У меня недостаточно прав.")

    except:
        await message.answer("Что-то пошло не так.")


@dp.message_handler(IsGroup(), Command("unmute", prefixes="!/"), AdminFilter())
async def unmute_member(message: types.Message):
    ReadOnlyPremissions = types.ChatPermissions(
        can_send_messages=True,
        can_send_media_messages=True,
        can_send_polls=True,
        can_send_other_messages=True
    )
    try:
        await message.chat.restrict(user_id=message.from_user.id, permissions=ReadOnlyPremissions, until_date=0)
        await message.reply(f"Пользователь {get_mention(message)} размучен")
    except BadRequest:
        await message.answer("У меня не получилось это сделать")
  

# BAN
@dp.message_handler(IsGroup(), Command("ban", prefixes="!/"), AdminFilter())
async def ban_member(message: types.Message):
    try:
        await message.chat.kick(user_id=message.reply_to_message.from_user.id)
        await message.reply(f"Пользователь {get_mention(message)} забанен")
    except BadRequest:
        await message.answer("У меня не получилось это сделать")

# UNBAN
@dp.message_handler(IsGroup(), Command("unban", prefixes="!/"), AdminFilter())
async def ban_member(message: types.Message):
    try:
        await message.chat.unban(user_id=message.reply_to_message.from_user.id)
        await message.reply(f"Пользователь {get_mention(message)} разбанен")
    except BadRequest:
        await message.answer("У меня не получилось это сделать")