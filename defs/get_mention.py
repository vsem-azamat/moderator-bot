from aiogram import types


def get_mention(message: types.Message):
    try:
        return message.reply_to_message.from_user.get_mention(as_html=True)
    except:
        return message.reply_to_message.from_user.first_name
