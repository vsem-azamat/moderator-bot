import re
from aiogram import types
from aiogram.dispatcher.filters import Command

from loader import dp, bot
from filters import SuperAdmins, IsGroup, AdminFilter

from db.sql_aclhemy import db


# GLOBAL ADMIN SETTINGS
@dp.message_handler(Command('admin', prefixes='!/'), SuperAdmins())
async def new_admin(message: types.Message):
    await message.reply(db.settings_gl_admins(message.from_user.id, message.text))


# WELCOME COMMANDS
@dp.message_handler(Command("welcome", prefixes="!/"), IsGroup(), AdminFilter())
async def welcome_change(message: types.Message):
    param = message.text.partition(" ")[2]
    await message.reply(db.welcome_command(message.chat.id, param))


# COMMAND SETTINGS
@dp.message_handler(IsGroup(), Command('list_com', prefixes='!/'), AdminFilter())
async def command_list(message: types.Message):
    db.check_chat(message.chat.id)
    inline_b = db.command_list()
    await message.reply("<b>Список комманд:</b>", reply_markup=inline_b)


@dp.callback_query_handler(regexp=r"^comm_")
async def command_callback(callback: types.CallbackQuery):
    command = callback.data[7:]
    state = int(callback.data[5:6])
    state_invert = {1: False, 0: True}.get(state)
    # print(state_invert)
    db.command_update_state(command, state_invert)

    inline_b = db.command_list()
    await bot.edit_message_reply_markup(callback.message.chat.id, callback.message.message_id,
                                        reply_markup=inline_b)
