
# list1 = [i for i in range(10)]
# x = [list.pop(i) for i in list1 if len(list1) > 1]

# print(x)



f1 = ('first', 'second','три',"четыре","пять")
f2 = (1, 2, 3, 4, 5 ) 



def inline_key(l_text: tuple, l_callback: tuple, row_width: int = 1):
    r = {"inline_keyboard": 
            [
                [[{text:callback}] for text, callback in zip(r_text, r_callback)] for r_text, r_callback in zip(l_text, l_callback)   
            ] 
        }
    return r
# print(inline_key(f1, f2))


def test2(l_text: tuple, l_callback: tuple, width: int = 3):
    res = []
    for i in range(int(len(l_text)/width)):
        for text, callback in zip(l_text[i*width:i*width+width], l_callback[i*width:i*width+width]):
            res.append({text:callback})
    return res


print(test2(f1,f2,2))
