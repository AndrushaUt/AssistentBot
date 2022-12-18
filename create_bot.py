from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import sqlalchemy as db

storage = MemoryStorage()
bot = Bot(token='5781824062:AAFSemAC-j7jbBzE5XrYxCNbVAf5FFKagJY')
dp = Dispatcher(bot, storage=storage)
engine = db.create_engine('sqlite:///data_base.db')
connection = engine.connect()
metadata = db.MetaData()

assistants = db.Table(
    'assistants',
    metadata,
    db.Column('assistant_name', db.Text),
    db.Column('assistant_id', db.Text),
    db.Column('subject_name', db.Text),
    db.Column('group_id', db.Text)
)

groups = db.Table(
    'groups',
    metadata,
    db.Column('student_id', db.Text),
    db.Column('student_name', db.Text),
    db.Column('group_id', db.Text)
)

subjects = db.Table(
    'subjects',
    metadata,
    db.Column('assistant_id', db.Text),
    db.Column('group_id', db.Text),
    db.Column('subject_id', db.Text),
    db.Column('table_name', db.Text),
    db.Column('table_href', db.Text)
)

personal_deadlines = db.Table(
    'personal_deadlines',
    metadata,
    db.Column('deadline_end_time', db.TIMESTAMP),
    db.Column('subject_name', db.Text),
    db.Column('student_name', db.Text),
    db.Column('deadline_content', db.Text),
    db.Column('is_done', db.Boolean, default=False),
    db.Column('is_announced', db.Boolean, default=False)
)

metadata.create_all(engine)
insertion_query = assistants.insert().values([
    {"assistant_name": "Уткин Андрей Сергеевич", "assistant_id": "398474393",
     "subject_name": "матан", "group_id": "БПМИ2112"},
    {"assistant_name": "Уткин Андрей Сергеевич", "assistant_id": "398474393",
     "subject_name": "python", "group_id": "БПМИ2112"},
    {"assistant_name": "Уткин Андрей Сергеевич", "assistant_id": "398474393",
     "subject_name": "теорвер", "group_id": "БПМИ218"},
])

insertion_query2 = groups.insert().values([
    {"student_name": "Уткин Андрей Сергеевич", "student_id": "398474393",
     "group_id": "БПМИ2112"}
])

#для тестирования
# connection.execute(insertion_query)
# connection.execute(insertion_query2)
