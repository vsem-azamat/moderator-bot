import math

class GenButtons:

    @classmethod
    def __json(cls, l_dict:dict, row_q:int, row_w:int) -> list:
        "Sort dicts for row and wight"
        return [l_dict[i*row_w:i*row_w + row_w] for i in range(row_q)]


    @classmethod
    def inline_b(cls, l_text:list, l_callback:list, row_w:int=1) -> dict:
        "Generate custom inline button"
        len_list = len(l_text)
        row_q = math.ceil(len_list/row_w)
        l_dict = [{"text": text, "callback_data": callback} for text, callback in zip(l_text, l_callback)]
        return {"row_wight": row_w, "inline_keyboard": cls.__json(l_dict, row_q, row_w)}


    @classmethod
    def default_b(cls, l_text:list, row_w:int) -> dict:
        "Generate custom default button"
        len_list = len(l_text)
        row_q = math.ceil(len_list/row_w)
        l_dict = [{"text": text, } for text in l_text]
        return {"keyboard": cls.__json(l_dict, row_q, row_w), "resize_keyboard": True}

genButton = GenButtons()