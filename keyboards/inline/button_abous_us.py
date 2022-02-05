from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

about_us = InlineKeyboardMarkup(row_wight=1,
                              inline_keyboard=[
                                  [
                                      InlineKeyboardButton(
                                          text='Центральный канал',
                                          url='t.me/Czech_Media'
                                      )
                                  ],
                                  [
                                      InlineKeyboardButton(
                                          text='Основной чат',
                                          url='t.me/czechopen'
                                      )
                                  ]

                              ])
