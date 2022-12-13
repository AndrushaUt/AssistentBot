from aiogram import types
from aiogram.utils import executor
from create_bot import dp
from aiogram.dispatcher.filters import Text

from keyboards.start_kb import kb_start

active_session = False


async def on_startup(_):
    print('Бот запущен')


@dp.message_handler(commands="start")
async def cm_start(message: types.Message):
    await message.reply("Ты кто?", reply_markup=kb_start)


@dp.message_handler(Text("Выйти"))
async def cm(message: types.Message):
    await message.answer("Ты кто?", reply_markup=kb_start)


@dp.message_handler(content_types='text')
async def funct(message: types.Message):
    print(message.text)


executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
