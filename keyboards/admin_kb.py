from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

kb_admin = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
btn1 = KeyboardButton("Добавить предмет")
btn2 = KeyboardButton("Создать объявление")
btn3 = KeyboardButton("Выйти")
kb_admin.add(btn1, btn2, btn3)


kb_cancel = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
btn1 = KeyboardButton("Отмена")
kb_cancel.add(btn1)


def get_kb_buttons(list_of_names):
    my_kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for name in set(list_of_names):
        btn = KeyboardButton(name[0])
        my_kb.add(btn)
    my_kb.add(KeyboardButton("Отмена"))
    return my_kb

