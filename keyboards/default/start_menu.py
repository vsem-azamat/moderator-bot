from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

bt11 = '💬Чаты по вузам'
bt12 = '👩‍🎓Репетиторы'

bt21 = '📢Каналы'
bt22 = '🛍️Рынок'

# bt31 = '💇Предложить услуги'
bt32 = 'ℹ️О нас!'

start_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=bt12)
        ],
        [
            KeyboardButton(text=bt11),
            KeyboardButton(text=bt21)


        ],
        [
            # KeyboardButton(text=bt31),
            KeyboardButton(text=bt22),
            KeyboardButton(text=bt32),
        ],
    ],
    resize_keyboard=True
)

# skazka_k = ReplyKeyboardMarkup(
# keyboard=[
#         [
#             KeyboardButton(text='Да'),
#             KeyboardButton(text="Нет")
#         ],
#     ],
#     resize_keyboard=True
# )