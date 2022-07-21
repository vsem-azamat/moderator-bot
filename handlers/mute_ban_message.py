from defs import get_mention, mute_date_calc

from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.utils import exceptions

from filters import IsGroup, AdminFilter, SuperAdmins
from app import dp, bot
from db.sql_aclhemy import db


# MUTE and UNMUTE
@dp.message_handler(IsGroup(), Command("mute", prefixes='!/'), AdminFilter())
async def mute_member(message: types.Message):
    mute_date = await mute_date_calc(message.text)

    ReadOnlyPremissions = types.ChatPermissions(
        can_send_messages=False,
        can_send_media_messages=False,
        can_send_polls=False,
        can_send_other_messages=False
    )

    try:
        await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id,
                                       permissions=ReadOnlyPremissions,
                                       until_date=mute_date['until_date'])
        time = mute_date.get('time')
        unit = mute_date.get('unit', 'm')
        until_date = mute_date['until_date'].strftime("%Y-%m-%d %H:%M:%S")

        mute_text = f"{get_mention(message.reply_to_message)} в муте на {time} {unit}!\n\nДата размута: {until_date}"
        await message.reply(mute_text)

    except AttributeError:
        await message.answer("Примените команду к сообщение человека, которого нужно замутить.")

    except exceptions.CantRestrictChatOwner:
        await message.answer("У меня недостаточно прав.")

    except exceptions.BadRequest as err:
        await message.answer(f"Что-то пошло не так.\n\n{err}")


@dp.message_handler(IsGroup(), Command("unmute", prefixes="!/"), AdminFilter())
async def unmute_member(message: types.Message):
    ReadOnlyPremissions_OFF = types.ChatPermissions(
        can_send_messages=True,
        can_send_media_messages=True,
        can_send_polls=True,
        can_send_other_messages=True
    )
    try:
        await message.chat.restrict(message.reply_to_message.from_user.id, permissions=ReadOnlyPremissions_OFF,
                                    until_date=0)
        await message.reply(f"Пользователь {get_mention(message.reply_to_message)} размучен")
    except exceptions.BadRequest:
        await message.answer("У меня не получилось это сделать")


# BAN
@dp.message_handler(IsGroup(), Command("ban", prefixes="!/"), AdminFilter())
async def ban_member(message: types.Message):
    try:
        await message.chat.kick(user_id=message.reply_to_message.from_user.id)
        await message.reply(f"Пользователь {get_mention(message.reply_to_message)} забанен")
    except exceptions.BadRequest:
        await message.answer("У меня не получилось это сделать")


# UNBAN
@dp.message_handler(IsGroup(), Command("unban", prefixes="!/"), AdminFilter())
async def ban_member(message: types.Message):
    try:
        await message.chat.unban(user_id=message.reply_to_message.from_user.id)
        await message.reply(f"Пользователь {get_mention(message.reply_to_message)} разбанен")
    except exceptions.BadRequest:
        await message.answer("У меня не получилось это сделать")


@dp.message_handler(Command('fullban', prefixes='!/'), SuperAdmins())
async def full_ban(message: types.Message):
    if message.reply_to_message:
        id_user = message.reply_to_message.from_user.id
        text = f"{get_mention(message.reply_to_message)} добавлен в черный список."
    else:
        id_user = message.text.split()[1]
        text = f"Пользователь с id: {id_user} добавлен в черный список."

    for id_chat in db.get_chat_list():
        try:
            await bot.ban_chat_member(id_chat, id_user)
        except:
            pass
    await message.reply(text)
    db.change_black_list(message.reply_to_message.from_user.id)

