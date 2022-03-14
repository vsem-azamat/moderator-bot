import asyncio
from aiogram import types
from aiogram.dispatcher.filters import Command

from filters import IsGroup, AdminFilter

from loader import dp, bot
from db.sql_aclhemy import SqlAlchemy, db

from defs import gen_button


# WELCOME MESSAGE
@dp.message_handler(IsGroup(), content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def new_member(message: types.Message):
    user_info = db.check_user(message.from_user.id)
    # if user in black list
    if user_info.get('black_list', False): 
        await bot.kick_chat_member(message.chat.id, message.from_user.id)
        await message.delete()
    
    else:
        welc_info = db.welcome_message(message.chat.id)
        db.add_new_user(message.from_user.id, welc_info['state_func'])

        # welcome message is Activate
        if welc_info['state_func'] is True: 
            
            # only welcome text
            if welc_info['state_test'] is False or user_info['verify']:
                welcome = await bot.send_message(message.chat.id, 
                    f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>", 
                    parse_mode="HTML")

            # text and verify test
            else:
                ReadOnlyPremissions_ON = types.ChatPermissions(
                    can_send_messages=False,
                    can_send_media_messages=False,
                    can_send_polls=False,
                    can_send_other_messages=False
                )
                await message.chat.restrict(user_id=member_id, permissions=ReadOnlyPremissions_ON)
                welcome = await bot.send_message(messahe.chat.id,
                    f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>", 
                    parse_mode="HTML", 
                    reply_markup=gen_button.inline_b(['I am not a bot'],['not_bot']))  
                    
            await asyncio.sleep(welc.get('time_delete', 60))
            await welcome.delete()
            await message.delete()
            
            # member is not a bot
            if db.check_verify(id_tg):
                ReadOnlyPremissions_OFF = types.ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_polls=True,
                    can_send_other_messages=True
                )
                await bot.restrict(message.from_user.id, ReadOnlyPremissions_OFF, until_date=0)
        
            # member is a bot
            else:
                await bot.kick_chat_member(message.chat.id, message.from_user.id)

        # welcome message is not Activate
        else:
            pass


@dp.callback_query_handler(lambda c: c.data == 'not_bot')
async def not_bot(callback: types.CallbackQuery):
    await callback.answer('Thanks! Welcome to the club!')
    db.change_verify(callback.from_user.id, update=True)


# ACTIVATE WELCOME
@dp.message_handler(Command("welcome", prefixes="!/"), IsGroup(), AdminFilter())
async def welcome_change(message: types.Message):
    param = message.text.partition(" ")[2]
    await message.reply(db.welcome_command(message.chat.id, param))
    
