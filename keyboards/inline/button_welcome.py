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

# print(welcome)


{"inline_keyboard": 
    [
        [
            {"text": "⬅", "callback_data": "page_back"}, 
            {"text": "➡", "callback_data": "page_next"}
        ]
    ]
}


f1 = ('first', 'second')
f2 = (1, 2) 

def inline_key(list_text: tuple, list_callback: tuple, row_width: int = 1):
    r = {"inline_keyboard": 
            [
              [  
                {list_text[_+i]: list_callback[_+i]} for i in range(2)
              ] if _ % 2 == 0 else [{list_text[_]: list_callback[_]}] for _ in range(len(zip(list_text, list_callback)))
            ]
        }
    return r
print(inline_key(f1, f2))

# def inline_k(l_text: tuple, l_callback: tuple, row_width: int = 1):   
#     x = []
#     y = []
#     q = int(len(l_text/2))
#     w = len
#     for i in range():
#         l_zip = 
#         y.append({text:callback} for text, callback in zip(l_text, l_callback))        
#     return r
л