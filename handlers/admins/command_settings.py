import re

from aiogram import types
from aiogram.dispatcher.filters import Command

from loader import dp, bot
from filters import SuperAdmins

from db.sql_aclhemy import db

@dp.message_handler(Command('setcom', prefixes='!/'), SuperAdmins())
async def setcom(message: types.Message):
    command_parse = re.compile(r"(!setcom|/setcom) ?([\w+\W])?")
    parsed = command_parse.match(message)
    command_name = parsed.group(2)

    # message_l = message.text.split(' ')
    # command = message_l[1]
    # state = {'on': True, 'off': False}.get(message_l[2].lower(), False)
    # chat_id = message.chat.id

    try:
        sql = """
            UPDATE command_states 
            SET id_chat=:chat_id, state=:state 
            WHERE id_command=(
                SELECT id 
                FROM commands
                WHERE command=:command
                )
        """
        db.execute(sql, chat_id=chat_id, state=state, command=command_name)
        await message.reply("Комманда выполнена")

    except Exception as e:
        await message.reply(f"Что то пошло не так!\n\nОшибка:\n{e}")