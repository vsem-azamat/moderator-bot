from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

school_chat = InlineKeyboardMarkup(row_wight=2,
                                   inline_keyboard=[
                                       [
                                           InlineKeyboardButton(
                                               text='ČVUT',
                                               url='t.me/cvut_chat'
                                           ),
                                           InlineKeyboardButton(
                                               text='VŠE',
                                               url='t.me/vse_chat'
                                           )

                                       ],
                                       [
                                           InlineKeyboardButton(
                                               text='Karlov',
                                               url='t.me/karlov_chat'
                                           ),
                                           InlineKeyboardButton(
                                               text='ČZU',
                                               url='t.me/czu_chat'
                                           )
                                       ],
                                       [
                                           InlineKeyboardButton(
                                               text='VŠCHT',
                                               url='t.me/vscht_chat'
                                           ),
                                           InlineKeyboardButton(
                                               text='VUT',
                                               url='t.me/vut_chat'
                                           )
                                       ],
                                       [
                                           InlineKeyboardButton(
                                               text='Masaryk',
                                               url='t.me/masaryk_chat'
                                           ),
                                           InlineKeyboardButton(
                                               text='GoStudy',
                                               url='t.me/Gostudy_20'
                                           )
                                       ],
                                       [
                                           InlineKeyboardButton(
                                               text='Центральный чат',
                                               url='t.me/czechopen'
                                           )
                                       ],
                                       [
                                           InlineKeyboardButton(
                                               text='Discord',
                                               url='discord.gg/YdtJenAsqp'
                                           )
                                       ]
                                   ])
