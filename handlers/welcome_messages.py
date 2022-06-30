import asyncio
from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.utils import exceptions

from filters import IsGroup

from loader import dp, bot
from db.sql_aclhemy import db

from defs import genButton


# WELCOME MESSAGE
@dp.message_handler(IsGroup(), Command('welcome_test', prefixes='!/'))
# @dp.message_handler(IsGroup(), content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def new_member(message: types.Message):
    user_info = db.check_user(message.from_user.id)
    # if user in black list
    if user_info.get('black_list', False):
        await bot.kick_chat_member(message.chat.id, message.from_user.id)
        await message.delete()

    else:
        welcome_info = db.welcome_message(message.chat.id)
        db.add_new_user(message.from_user.id, welcome_info['state_func'])

        # welcome message is Activate
        if welcome_info['state_func'] is True:
            # user_name_link = f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>"
            inline_markup = None
            # verify test
            if welcome_info['state_test'] or user_info['verify'] is False:
                ReadOnlyPremissions_ON = types.ChatPermissions(
                    can_send_messages=False,
                    can_send_media_messages=False,
                    can_send_polls=False,
                    can_send_other_messages=False
                )
                await message.chat.restrict(user_id=message.from_user.id, permissions=ReadOnlyPremissions_ON)

                inline_markup = genButton.inline_b(['I am not a bot'], [f'not_bot'])
            welcome = await message.reply(welcome_info['text'], parse_mode="HTML", reply_markup=inline_markup)

            await asyncio.sleep(welcome_info.get('time_delete', 60))
            await welcome.delete()
            await message.delete()

            # user is not a bot
            try:
                if db.check_verify(message.from_user.id):
                    ReadOnlyPremissions_OFF = types.ChatPermissions(
                        can_send_messages=True,
                        can_send_media_messages=True,
                        can_send_polls=True,
                        can_send_other_messages=True
                    )
                    await message.chat.restrict(message.from_user.id, ReadOnlyPremissions_OFF)

                # user is a bot
                else:
                    unban_message = await bot.unban_chat_member(message.chat.id, message.from_user.id)
                    await unban_message.delete()

            except exceptions.CantRestrictChatOwner as err:
                error_message = await message.answer(f'Что то пошло не так: \n\n{err}')
                await asyncio.sleep(10)
                await error_message.delete()


@dp.callback_query_handler(lambda c: c.data == 'not_bot')
async def not_bot(callback: types.CallbackQuery):
    await callback.answer('Thanks! Welcome to the club!')
    db.change_verify(callback.from_user.id, True)
    ReadOnlyPremissions_OFF = types.ChatPermissions(
        can_send_messages=True,
        can_send_media_messages=True,
        can_send_polls=True,
        can_send_other_messages=True
    )
    await bot.restrict_chat_member(callback.message.chat.id, callback.from_user.id, ReadOnlyPremissions_OFF)


