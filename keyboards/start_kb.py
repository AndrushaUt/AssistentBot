from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


kb_start = ReplyKeyboardMarkup(resize_keyboard=True)
btn1 = KeyboardButton("Студент")
btn2 = KeyboardButton("Accистент")
kb_start.add(btn1, btn2)
