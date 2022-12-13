from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import psycopg
storage = MemoryStorage()
bot = Bot(token='5781824062:AAFSemAC-j7jbBzE5XrYxCNbVAf5FFKagJY')
dp = Dispatcher(bot, storage = storage)
connection = psycopg.connect(
    host='127.0.0.1',
    user='postgres',
    password='qwerty',
    dbname='test_database'
)
connection.autocommit = True
