from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def create_kb_buttons(l: list) -> ReplyKeyboardMarkup:
    set_subject = set()
    temp_l = list()
    for but in l:
        set_subject.add(but[0])
    for but in set_subject:
        temp_l.append(KeyboardButton(but))
    temp_l.append(KeyboardButton("Отмена"))
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).row(*temp_l)
    return keyboard


kb_client = ReplyKeyboardMarkup(resize_keyboard=True)
btn1 = KeyboardButton("Получить оценку")
btn2 = KeyboardButton("Дедлайны")
btn4 = KeyboardButton("Расписание")
btn3 = KeyboardButton("Выйти")
kb_client.add(btn1, btn2, btn4, btn3)

kb_timetable_client = ReplyKeyboardMarkup(resize_keyboard=True)
btntoday = KeyboardButton('Сегодня')
btnweek = KeyboardButton('Неделя')
btncancel = KeyboardButton('Отмена')
kb_timetable_client.add(btntoday,btnweek,btncancel)

kb_deadlines_client = ReplyKeyboardMarkup(resize_keyboard=True)
btndead1 = KeyboardButton("Получить дедлайны")
btndead2 = KeyboardButton("Создать свой дедлайн")
btndead3 = KeyboardButton("Отметить дедлайн")
kb_deadlines_client.row(btndead1, btndead2, btndead3,KeyboardButton("Отмена"))
