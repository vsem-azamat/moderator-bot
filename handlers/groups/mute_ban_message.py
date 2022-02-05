import asyncio
import datetime
import re

from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.utils.exceptions import BadRequest

from filters import IsGroup, AdminFilter
from loader import dp, bot


# MUTE and UNMUTE
@dp.message_handler(IsGroup(), Command("mute", prefixes='!/'), AdminFilter())
async def mute_member(message: types.Message):
    member = message.reply_to_message.from_user
    member_id = message.reply_to_message.from_user.id
    chat_id = message.chat.id
    command_parse = re.compile(r"(!mute|/mute) ?(\d+)? ?([\w+\D ]+)?")
    parsed = command_parse.match(message.text)
    time = parsed.group(2)
    comment = parsed.group(3)
    if time is None:
        time = int(5)
    else:
        time = int(time)
    until_date = datetime.datetime.now() + datetime.timedelta(minutes=time)

    ReadOnlyPremissions = types.ChatPermissions(
        can_send_messages=False,
        can_send_media_messages=False,
        can_send_polls=False,
        can_send_other_messages=False
    )
    try:
        await bot.restrict_chat_member(chat_id=chat_id, user_id=member_id, permissions=ReadOnlyPremissions,
                                       until_date=until_date)
        # for change words "минут"
        time_for_text = int(time)
        # time_for_text = int(time_for_text[-1])
        if time_for_text < 5:
            bukva = "ы"
        else:
            bukva = ""
        if comment is None:
            mute_text = f"Пользователь {member.get_mention(as_html=True)} в муте на {time} минут{bukva}."
        elif comment is not None:
            mute_text = f"Пользователь {member.get_mention(as_html=True)} в муте на {time} минут{bukva}. \nПричина: {comment} "
        mute_message = await message.reply(mute_text)
        await asyncio.sleep(60)
        await mute_message.delete()

    except BadRequest:
        print(BadRequest
              )
        await message.answer("Пользователь является администратором")


@dp.message_handler(IsGroup(), Command("unmute", prefixes="!/"), AdminFilter())
async def unmute_member(message: types.Message):
    member = message.reply_to_message.from_user
    member_id = member.id

    ReadOnlyPremissions = types.ChatPermissions(
        can_send_messages=True,
        can_send_media_messages=True,
        can_send_polls=True,
        can_send_other_messages=True
    )
    try:
        await message.chat.restrict(user_id=member_id, permissions=ReadOnlyPremissions, until_date=0)
        unmute_message = await message.reply(f"Пользователь {member.get_mention(as_html=True)} размучен")
    except BadRequest:
        await message.answer("Ошибка размута")
    await asyncio.sleep(60)
    await unmute_message.delete()


# BAN and UNBAN
@dp.message_handler(IsGroup(), Command("ban", prefixes="!/"), AdminFilter())
async def ban_member(message: types.Message):
    member = message.reply_to_message.from_user
    member_id = member.id
    await message.chat.kick(user_id=member_id)
    ban_message = await message.reply(f"Пользователь {member.get_mention(as_html=True)} забанен")
    await asyncio.sleep(120)
    await ban_message.delete()


@dp.message_handler(IsGroup(), Command("unban", prefixes="!/"), AdminFilter())
async def ban_member(message: types.Message):
    member = message.reply_to_message.from_user
    member_id = member.id
    await message.chat.unban(user_id=member_id)
    unban_message = await message.reply(f"Пользователь {member.get_mention(as_html=True)} разбанен")
    await asyncio.sleep(60)
    await unban_message.delete()


# LEFT OF CHAT
# @dp.message_handler(IsGroup(), content_types=types.ContentType.LEFT_CHAT_MEMBER)
# async def push_ban_member(message: types.Message):
#     if message.left_chat_member.id == message.from_user.id:  # сам вышел
#         return
#     elif message.from_user.id == (await bot.me).id:  # бот забанил
#         return
#     else:
#         leave_message = await message.reply(f"{message.left_chat_member.full_name} был удалён из чата"
#                                             f" администратором {message.from_user.full_name}.")
#         await asyncio.sleep(60)
#         await leave_message.delete()
