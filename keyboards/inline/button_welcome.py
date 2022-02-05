from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


welcome = InlineKeyboardMarkup(row_width=1,
                               inline_keyboard=[
                                   [
                                       InlineKeyboardButton(
                                           text="I'm not a bot",
                                           callback_data='not_bot'
                                       )
                                   ]
                               ])
