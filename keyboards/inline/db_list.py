from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# from handlers.users.new import next_back_callback


next = InlineKeyboardMarkup(row_width=1,
                            inline_keyboard=[
                                [
                                    InlineKeyboardButton(
                                        text='➡',
                                        callback_data='page_next'
                                    )
                                ]
                            ])

back = InlineKeyboardMarkup(row_width=1,
                            inline_keyboard=[
                                [
                                    InlineKeyboardButton(
                                        text='⬅',
                                        callback_data='page_back'
                                    )
                                ]
                            ])

next_back = InlineKeyboardMarkup(row_width=2,
                                 inline_keyboard=[
                                     [
                                         InlineKeyboardButton(
                                             text='⬅',
                                             callback_data='page_back'
                                         ),
                                         InlineKeyboardButton(
                                             text='➡',
                                             callback_data='page_next'
                                         )
                                     ]

                                 ])
