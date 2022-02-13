import math

def gen_inline_button(tuple_text: list, tuple_callback: list,
                      row_wight: int = 1, ):
    len_list = len(tuple_text)
    row_quantity = math.ceil(len_list / row_wight)

    list_dict = []
    for i in range(len_list):
        list_dict.append({"text": f"{tuple_text[i]}", "callback_data": f"{tuple_callback[i]}"})

    finale_list = []
    for j in range(row_quantity):
        j = j * row_wight
        finale_list.append(list_dict[j:j + row_wight])

    return {"row_wight": row_wight, "inline_keyboard": finale_list}


def gen_default_button(tuple_text: list, row_wight: int = 1):
    len_list = len(tuple_text)
    row_quantity = math.ceil(len_list / row_wight)

    list_dict = []
    for text in tuple_text:
        list_dict.append({"text": f"{text}"})

    finale_list = []
    for j in range(row_quantity):
        j = j * row_wight
        finale_list.append(list_dict[j:j + row_wight])

    return {"keyboard": finale_list, "resize_keyboard": True}


class GenButtons():

    def default_b(l_text, width):
        
        return {"keyboard:": finale_list, "resize_keyboard": True}