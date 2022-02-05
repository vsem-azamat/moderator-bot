import asyncio

from aiogram import types

from aiogram.dispatcher.filters import Command
from filters import IsGroup, AdminFilter
from keyboards.inline.button_welcome import welcome

from loader import dp, bot
# from defs.def_add_users_chats import
from defs.def_welcome_message import welcome_from_sql, welcome_setting


# WELCOME MESSAGE
@dp.message_handler(IsGroup(), content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def new_member(message: types.Message):
    # id_user = message.new_chat_members[0].id
    dates_from_sql = welcome_from_sql(message.chat.id)  # chat_id, text, on_off, button
    welcome_text = await message.reply(dates_from_sql[1])

    # if dates_from_sql[3] == 1:
    #     welcome_text = await message.reply(dates_from_sql[1], reply_markup=welcome)
    # else:
    #     welcome_text = await message.reply(dates_from_sql[1])

    await asyncio.sleep(20)
    await welcome_text.delete()


# ACTIVATE WELCOME
@dp.message_handler(IsGroup(), Command("welcome", prefixes="!/"), AdminFilter())
async def welcome_change(message: types.Message):
    welcome_text = message.text.partition(" ")[2]
    await message.reply(welcome_setting(message.chat.id, welcome_text))


# ACTIVATE FACE CONTROL
# @dp.message_handler(IsGroup(), Command("facecontrol", prefixes="!/"), AdminFilter())
# async def welcome_button(message: types.Message):
#     text, button_state = w_button(chat_id=message.chat.id)
#     await message.reply(text=text)


# FACE CONTROL BUTTON TRIGGER
# @dp.callback_query_handler(IsGroup(), regexp=r"^not_bot")
# async def bot_control(callback_query: types.CallbackQuery):
#     states = face_state(callback_query.message.chat.id, callback_query.from_user.id)
#     if states == 1:
#         await bot.edit_message_reply_markup(message_id=callback_query.message.message_id,
#                                             reply_markup=None)
#     else:
#         pass
#
#     await callback_query.message.delete()
