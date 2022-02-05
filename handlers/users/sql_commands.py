from aiogram import types
from aiogram.dispatcher.filters import Command

from db.sq_lite import cursor, conn
from filters import SuperAdmins
from loader import dp, bot


@dp.message_handler(Command("sql", prefixes='!/'), SuperAdmins())
async def edit(message: types.Message):
    try:
        sql_command = message.text.partition(" ")[2]
        cursor.execute(sql_command)
        catalog = cursor.fetchall()
        conn.commit()
        if len(catalog) is not None:
            print(1)
            pass
        else:
            print(2)
            catalog = "Выполнено."
        await bot.send_message(chat_id=message.chat.id, text=catalog)

    except Exception as error:
        await bot.send_message(chat_id=message.chat.id, text=error)

