from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import psycopg
storage = MemoryStorage()
bot = Bot(token='5438351319:AAFxysJ5uGOYwVn23v8pPgXdkkz-kplKwCc')
dp = Dispatcher(bot, storage = storage)
connection = psycopg.connect(
    host='127.0.0.1',
    user='postgres',
    password='qwerty',
    dbname='test_database'
)
connection.autocommit = True