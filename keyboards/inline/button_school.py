from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

school_teacher1 = InlineKeyboardMarkup(row_wight=2,
                                       inline_keyboard=[
                                           [
                                               InlineKeyboardButton(
                                                   text='ČVUT',
                                                   callback_data='list_cvut'
                                               ),
                                               InlineKeyboardButton(
                                                   text='VŠE',
                                                   callback_data='list_vse'
                                               )

                                           ],
                                           [
                                               InlineKeyboardButton(
                                                   text='Karlov',
                                                   callback_data='list_uk'
                                               ),
                                               InlineKeyboardButton(
                                                   text='ČZU',
                                                   callback_data='list_czu'
                                               )
                                           ],
                                           [
                                               InlineKeyboardButton(
                                                   text='VUT',
                                                   callback_data='list_vut'
                                               ),
                                               InlineKeyboardButton(
                                                   text='Masaryk',
                                                   callback_data='list_masaryk'
                                               )
                                           ],
                                           [
                                                InlineKeyboardButton(
                                                    text='VŠCHT',
                                                    callback_data='list_vscht'
                                                ),
                                                InlineKeyboardButton(
                                                   text='Нострификация',
                                                   callback_data='list_nostr'
                                                )
                                           ],
                                           [
                                               # InlineKeyboardButton(
                                               #     text='Стать репетитором',
                                               #     callback_data='list_add'
                                               # ),
                                               InlineKeyboardButton(
                                                   text='По предметам🔃',
                                                   callback_data='sort_less'
                                               )
                                           ]
                                       ])

school_teacher2 = InlineKeyboardMarkup(row_width=2,
                                       inline_keyboard=[
                                           [
                                               InlineKeyboardButton(
                                                   text='Математика',
                                                   callback_data='list_math'
                                               ),
                                               InlineKeyboardButton(
                                                   text='Физика',
                                                   callback_data='list_fyz'
                                               ),
                                           ],
                                           [
                                               InlineKeyboardButton(
                                                   text='Программирование',
                                                   callback_data='list_prog'
                                               ),
                                               InlineKeyboardButton(
                                                   text='Статистика',
                                                   callback_data='list_stat'
                                               )
                                           ],
                                           [
                                               InlineKeyboardButton(
                                                   text='Экономика',
                                                   callback_data='list_eco'
                                               ),
                                               InlineKeyboardButton(
                                                   text='Право',
                                                   callback_data='list_prav'
                                               )
                                           ],
                                           [
                                               InlineKeyboardButton(
                                                   text='Биология',
                                                   callback_data='list_biol'
                                               ),
                                               InlineKeyboardButton(
                                                   text='Химия',
                                                   callback_data='list_chem'
                                               )
                                           ],
                                           [
                                               InlineKeyboardButton(
                                                   text='Чешский',
                                                   callback_data='list_czech'
                                               ),
                                               InlineKeyboardButton(
                                                   text='Английский',
                                                   callback_data='list_engl'
                                               )
                                           ],
                                           [
                                               InlineKeyboardButton(
                                                   text='Нострификация',
                                                   callback_data='list_nostr'
                                               )
                                           ],
                                           [
                                               InlineKeyboardButton(
                                                   text='По ВУЗ-ам🔃',
                                                   callback_data='sort_univ'
                                               )
                                           ]
                                       ])

test1 = InlineKeyboardMarkup(row_wight=1,
                             inline_keyboard=[
                                 [
                                     InlineKeyboardButton(
                                         text='cvut',
                                         callback_data='aboba cvut'
                                     )
                                 ]
                             ]
                             )
