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

    # if user in black list
    if db.black_list(message.from_user.id) is None: 
        await bot.kick_chat_member(message.chat.id, message.from_user.id)
        await message.delete()
    
    else:
        welc_dates = db.welcome_message(message.chat.id)
        db.new_chat_member(id_tg, welc_dates['state_func']) # add user if he is new

        
        # welcome message is Activate
        if welc_dates['state_func'] is True: 
            state_test = welc_dates['state_test']
            state_verify = db.check_verify(id_tg)
            
            # only welcome text
            if state_test is False or state_verify:
                
                message_welc = await message.reply(welc_dates['text'])
            
                await bot.send_message(message.chat.id, 
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
@dp.message_handler(IsGroup(), Command("welcome", prefixes="!/"), AdminFilter())
async def welcome_change(message: types.Message):
    welcome_text = message.text.partition(" ")[2]
    
    await message.reply(welcome_setting(message.chat.id, welcome_text))

