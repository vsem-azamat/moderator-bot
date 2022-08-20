import asyncio

from app import dp, bot
from aiogram import types, exceptions
from aiogram.dispatcher.filters import Command

from filters import SuperAdmins, IsGroup, AdminFilter
from db.sql_aclhemy import db
from defs import genButton, mute_date_calc, get_mention
from data.config import SUPER_ADMINS

# MUTE and UNMUTE
@dp.message_handler(IsGroup(), Command("mute", prefixes='!/'), AdminFilter())
async def mute_member(message: types.Message):
    mute_date = mute_date_calc(message.text)

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

        mute_text = f"{await get_mention(message.reply_to_message)} в муте на {time} {unit}!\n\nДата размута: {until_date}"
        await message.reply(mute_text)

    except AttributeError:
        await message.answer("Примените команду к сообщение человека, которого нужно замутить.")

    except exceptions.CantRestrictChatOwner:
        await message.answer("У меня недостаточно прав.")

    except exceptions.BadRequest as err:
        await message.answer(f"Что-то пошло не так:\n\n{err}")


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
        await message.reply(f"Пользователь {await get_mention(message.reply_to_message)} размучен")
    except exceptions.BadRequest:
        await message.answer("У меня не получилось это сделать")


# BAN
@dp.message_handler(IsGroup(), Command("ban", prefixes="!/"), AdminFilter())
async def ban_member(message: types.Message):
    try:
        await message.chat.kick(user_id=message.reply_to_message.from_user.id)
        await message.reply(f"Пользователь {await get_mention(message.reply_to_message)} забанен")
    except exceptions.BadRequest:
        await message.answer("У меня не получилось это сделать")


# UNBAN
@dp.message_handler(IsGroup(), Command("unban", prefixes="!/"), AdminFilter())
async def ban_member(message: types.Message):
    try:
        await message.chat.unban(user_id=message.reply_to_message.from_user.id)
        await message.reply(f"Пользователь {await get_mention(message.reply_to_message)} разбанен")
    except exceptions.BadRequest:
        await message.answer("У меня не получилось это сделать")


@dp.message_handler(Command('fullban', prefixes='!/'), SuperAdmins())
async def full_ban(message: types.Message):
    if message.reply_to_message:
        id_user = message.reply_to_message.from_user.id
        text = f"{await get_mention(message.reply_to_message)} добавлен в черный список."
    else:
        id_user = message.text.split()[1]
        text = f"Пользователь с id: {id_user} добавлен в черный список."

    for id_chat in await db.get_chat_list():
        try:
            await bot.ban_chat_member(id_chat, id_user)
        except:
            pass
    await message.reply(text)
    await db.change_black_list(message.reply_to_message.from_user.id)


# GLOBAL ADMIN SETTINGS
@dp.message_handler(Command('admin', prefixes='!/'), SuperAdmins())
async def new_admin(message: types.Message):
    await message.reply(await db.settings_gl_admins(message.from_user.id, message.text))


# WELCOME COMMANDS
@dp.message_handler(Command("welcome", prefixes="!/"), IsGroup(), AdminFilter())
async def welcome_change(message: types.Message):
    text = message.text.partition(" ")[2]
    await message.reply(await db.welcome_command(message.chat.id, text))


# COMMAND SETTINGS
@dp.message_handler(Command('list_com', prefixes='!/'), SuperAdmins())
async def command_list(message: types.Message):
    await db.check_chat(message.chat.id)
    inline_b = await db.command_list()
    await message.reply("<b>Список комманд:</b>", reply_markup=inline_b)


@dp.callback_query_handler(regexp=r"^comm_")
async def command_callback(callback: types.CallbackQuery):
    command = callback.data[7:]
    state = int(callback.data[5:6])
    state_invert = {1: False, 0: True}.get(state)
    await db.command_update_state(command, state_invert)

    inline_b = await db.command_list()
    await bot.edit_message_reply_markup(callback.message.chat.id, callback.message.message_id,
                                        reply_markup=inline_b)

# SEND DB TO CHAT
@dp.message_handler(Command("send_db", prefixes="!/"), SuperAdmins())
async def send_db(message: types.Message):
    await message.reply_document(open('db/moder_bot.db', 'rb'))


@dp.message_handler(Command('report', prefixes='!/'), IsGroup())
async def report(message: types.Message):
    if message.reply_to_message:
        try:
            message_link = f"<a href='{message.reply_to_message.url}'>ссылка</a>"
            chat_name = message.chat.title
            text = f"<b>Поступил репорт:</b>\n<b>Чат:</b> {chat_name}\n<b>Сообщение:</b> {message_link}"

            for id_admin in SUPER_ADMINS:
                b_text = ('Забанить', 'Мут', 'Удалить сообщение', 'Оставить')
                b_command = ('report_ban', 'report_mute', 'report_del', 'report_pass')
                rep_message_id = message.reply_to_message.message_id
                rep_user_id = message.reply_to_message.from_user.id
                rep_chat_id = message.reply_to_message.chat.id
                b_command = (f"{i} {rep_message_id} {rep_user_id} {rep_chat_id}" for i in b_command)
                buttons = await genButton.inline_b(b_text, b_command)

                await bot.send_message(id_admin, text, reply_markup=buttons)
                await bot.forward_message(id_admin, message.chat.id, message.reply_to_message.message_id)

        except Exception as err:
            for id_admin in SUPER_ADMINS:
                await bot.send_message(id_admin, err)

        message_send = await message.answer("Жалоба принята!\nСпасибо за уведомление!")
        await message.delete()

    else:
        message_send = await message.reply("Вы должны применить комманду на сообщение!")
    await asyncio.sleep(60)
    await message_send.delete()

# Гавно код - обязательно перепишу позже
@dp.callback_query_handler(regexp=r"^report_")
async def report(callback: types.CallbackQuery):
    await callback.answer()
    callback_data = callback.data[7:].split()
    command = callback_data[0]
    message_id = callback_data[1]
    user_id = callback_data[2]
    chat_id = callback_data[3]
    if command == "ban":
        await bot.ban_chat_member(chat_id, user_id)
    elif command == "mute":
        inline_b = await genButton.inline_b(('Mute: 60 m', 'Mute: 360 m', 'Mute: 1000 m'),
                                            (f"{i} {chat_id} {user_id}" for i in ('mute_60', 'mute_360', 'mute_1000')))
        await bot.edit_message_reply_markup(callback.message.chat.id, callback.message.message_id,
                                            reply_markup=inline_b)
    elif command == "del":
        await bot.delete_message(chat_id, message_id)
    elif command == "pass":
        await callback.message.delete()
    else:
        await callback.message.answer("Почини бота, клоун!")


@dp.callback_query_handler(regexp=r"mute_")
async def report_mute(callback: types.CallbackQuery):
    callback_data = callback.data[5:].split()
    time = callback_data[0]
    chat_id = callback_data[1]
    user_id = callback_data[2]
    ReadOnlyPremissions = types.ChatPermissions(
        can_send_messages=False,
        can_send_media_messages=False,
        can_send_polls=False,
        can_send_other_messages=False
    )
    until_date = mute_date_calc(f"!mute {time}")['until_date']
    await bot.restrict_chat_member(chat_id, user_id, ReadOnlyPremissions, until_date)
