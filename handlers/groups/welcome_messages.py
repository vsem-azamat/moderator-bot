import asyncio
from aiogram import types
from aiogram.dispatcher.filters import Command

from filters import IsGroup, AdminFilter
from keyboards.inline.button_welcome import welcome

from loader import dp, bot
from db.sql_aclhemy import SqlAlchemy, db

from defs.def_welcome_message import welcome_from_sql, welcome_setting


# WELCOME MESSAGE
@dp.message_handler(IsGroup(), content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def new_member(message: types.Message):
    
    
    if db.black_list(message.from_user.id) is None: # if user in black list
        await bot.kick_chat_member(message.chat.id, message.from_user.id)
        await message.delete()
    
    else: 
        welc = db.welcome_message(message.from_user.id, message.chat.id)
        
        if welc['state_func'] and not welc['state_test']:   # only welcome text
            message_welc = await message.reply(welc['text'])
        
        elif welc['state_func'] and welc['state_test']:     # text and verify test
            message_welc = await message.reply(welc['text'], reply_markup=welcome)  # заменить кнопку на тестовую
        
        try:
            await asyncio.sleep(welc.get('time_delete', 60))
            await welcome_we.delete()
        except:
            pass
        
@dp.callback_query_handler(lambda c: c.data == 'not_bot')
async def not_bot(message: types.Message):
    pass




# ACTIVATE WELCOME
@dp.message_handler(IsGroup(), Command("welcome", prefixes="!/"), AdminFilter())
async def welcome_change(message: types.Message):
    welcome_text = message.text.partition(" ")[2]
    await message.reply(welcome_setting(message.chat.id, welcome_text))

