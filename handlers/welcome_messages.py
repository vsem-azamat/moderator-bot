import asyncio
import datetime
import random

from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.utils import exceptions

from filters import IsGroup, Unmute

from app import dp, bot
from db.sql_aclhemy import db

from defs import genButton


# WELCOME MESSAGE
@dp.message_handler(IsGroup(), content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def new_member(message: types.Message):
    # if user in black list
    id_tg = message.new_chat_members[0].id
    state_user = await db.check_user(id_tg).get('black_list', False)
    if state_user:
        await bot.kick_chat_member(message.chat.id, id_tg)
        await message.delete()

    else:
        welcome_info = await db.welcome_message(id_tg)
        await db.add_new_user(id_tg, welcome_info['state_test'])
        user_info = await db.check_user(id_tg)

        # welcome message is Activate
        if welcome_info['state_func'] is True:
            # user_name_link = f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>"
            inline_markup = None
            # verify test
            if welcome_info['state_test'] and user_info['verify'] is False:
                ReadOnlyPremissions_ON = types.ChatPermissions(
                    can_send_messages=False,
                    can_send_media_messages=False,
                    can_send_polls=False,
                    can_send_other_messages=False
                )
                await message.chat.restrict(user_id=id_tg, permissions=ReadOnlyPremissions_ON)
                if welcome_info['state_test'] == 1:
                    inline_markup = await genButton.inline_b(["🔒I'm not a bot🔒"], [f"not_bot"])
                elif welcome_info['state_test'] == 2:
                    date = datetime.datetime.now().date()
                    random_dates = [date]

                    # to generate list of random dates
                    start_date = date - datetime.timedelta(days=90)
                    end_date = date + datetime.timedelta(days=90)
                    time_between_dates = end_date - start_date
                    days_between_dates = time_between_dates.days
                    for _ in range(4):
                        random_number_of_days = random.randrange(days_between_dates)
                        random_dates.append(start_date + datetime.timedelta(days=random_number_of_days))
                    random.shuffle(random_dates)
                    random_dates = list(map(str, random_dates))
                    random_dates.insert(0, '❗Today is:')
                    inline_markup = await genButton.inline_b(random_dates, random_dates, row_w=3)

            welcome = await message.reply(welcome_info['text'], parse_mode="HTML", reply_markup=inline_markup)

            await asyncio.sleep(welcome_info.get('time_delete', 60))
            await welcome.delete()
            await message.delete()

            # user is not a bot
            try:
                if await db.check_verify(id_tg):
                    ReadOnlyPremissions_OFF = types.ChatPermissions(
                        can_send_messages=True,
                        can_send_media_messages=True,
                        can_send_polls=True,
                        can_send_other_messages=True
                    )
                    await message.chat.restrict(id_tg, ReadOnlyPremissions_OFF)

                # user is a bot
                else:
                    await bot.unban_chat_member(message.chat.id, id_tg)

            except exceptions.CantRestrictChatOwner as err:
                error_message = await message.answer(f'Что то пошло не так: \n\n{err}')
                await asyncio.sleep(10)
                await error_message.delete()


@dp.callback_query_handler(Unmute())
async def not_bot(callback: types.CallbackQuery):
    await callback.answer('Thanks! Welcome to the club!')
    await db.change_verify(callback.from_user.id, True)
    ReadOnlyPremissions_OFF = types.ChatPermissions(
        can_send_messages=True,
        can_send_media_messages=True,
        can_send_polls=True,
        can_send_other_messages=True
    )
    await bot.restrict_chat_member(callback.message.chat.id, callback.from_user.id, ReadOnlyPremissions_OFF)


