from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from keyboards.admin_kb import kb_admin, get_kb_buttons, kb_cancel
from keyboards.start_kb import kb_start
from create_bot import connection
from aiogram import types
from create_bot import bot, dp

@dp.message_handler(Text("Accистент"))
async def cm(message: types.Message):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT assistant_name from assistants WHERE assistant_id =" + "'" + str(message.from_user.id) + "';")
        assistant_name = cursor.fetchone()
        if assistant_name:
            await message.answer(f"Вход выполнен...\nДобро пожаловать, {assistant_name[0]}", reply_markup=kb_admin)
        else:
            await message.answer("Вы не являетесь ассистентом", reply_markup=kb_start)


class FSMAdmin(StatesGroup):
    group_id = State()
    subject_name = State()
    amount_table = State()
    tables_names = State()
    tables_href = State()


@dp.message_handler(Text("Добавить предмет"), state=None)
async def add_subject(message: types.Message, state: FSMContext):
    with connection.cursor() as cursor:
        cursor.execute("SELECT group_id from assistants WHERE assistant_id =" + "'" + str(message.from_user.id) + "';")
        group_names = list(cursor.fetchall())
    if not group_names:
        await message.reply('Вы не ассистент', reply_markup=kb_admin)
    else:
        await message.reply('Выберите группу, которой хотите добавить предмет',
                            reply_markup=get_kb_buttons(group_names))
        async with state.proxy() as data:
            data['group_names'] = [item[0] for item in group_names]
        await FSMAdmin.group_id.set()


@dp.message_handler(state=FSMAdmin.group_id)
async def get_group(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        group_names = data['group_names']

    if message.text not in group_names:
        await message.answer('Вы не являетесь ассистентом этой группы', reply_markup=kb_admin)
        await state.finish()
        return

    async with state.proxy() as data:
        data['group_id'] = message.text

    with connection.cursor() as cursor:
        cursor.execute("SELECT subject_name from assistants WHERE assistant_id =" + "'" + str(message.from_user.id) + "' " + "AND group_id=" + "'" + message.text + "';")
        subject_names = list(cursor.fetchall())

    async with state.proxy() as data:
        data['subject_names'] = [item[0] for item in subject_names]

    await message.answer('Введите название предмета', reply_markup=get_kb_buttons(subject_names))
    await FSMAdmin.next()


@dp.message_handler(state=FSMAdmin.subject_name)
async def get_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        subject_names = data['subject_names']
    if message.text == 'Отмена':
        await message.answer('Процесс отменен', reply_markup=kb_admin)
        await state.finish()
    elif message.text not in subject_names:
        await message.answer('Вы не являетесь ассистентом этого предмета', reply_markup=kb_admin)
        await state.finish()
    else:
        async with state.proxy() as data:
            data['subject_name'] = message.text
        await message.answer('Введите количество таблиц', reply_markup=kb_cancel)
        await FSMAdmin.next()


@dp.message_handler(state=FSMAdmin.amount_table)
async def get_amount(message: types.Message, state: FSMContext):
    if message.text == 'Отмена':
        await message.answer('Процесс отменен', reply_markup=kb_admin)
        await state.finish()
    else:
        async with state.proxy() as data:
            data['amount_table'] = int(message.text)
        await message.answer('Введите через enter названия для таблиц(желательно одним словом)', reply_markup=kb_cancel)
        await FSMAdmin.next()


@dp.message_handler(state=FSMAdmin.tables_names)
async def get_table_name(message: types.Message, state: FSMContext):
    if message.text == 'Отмена':
        await message.answer('Процесс отменен', reply_markup=kb_admin)
        await state.finish()
    else:
        async with state.proxy() as data:
            data['tables_names'] = list(message.text.split('\n'))
        await message.answer('Введите через enter ссылки на таблицы в соответствующем порядке', reply_markup=kb_cancel)
        await FSMAdmin.next()


@dp.message_handler(state=FSMAdmin.tables_href)
async def get_table_href(message: types.Message, state: FSMContext):
    if message.text == 'Отмена':
        await message.answer('Процесс отменен', reply_markup=kb_admin)
    else:
        async with state.proxy() as data:
            data['tables_href'] = list(message.text.split('\n'))
            with connection.cursor() as cursor:
                for item in zip(data['tables_names'], data['tables_href']):
                    query = "INSERT INTO subjects (assistant_id, group_id, subject_id, table_name, table_href) VALUES ('" + str(
                        message.from_user.id) + "', '" + str(data['group_id']) + "', '" + str(
                        data['subject_name']) + "', '" + str(
                        item[0]) + "', '" + str(item[1]) + "');"
                    cursor.execute(query)

        await message.answer('Предмет успешно добавлен', reply_markup=kb_admin)
    await state.finish()


class FSMAnnounce(StatesGroup):
    group_id = State()
    subject = State()
    announce = State()


@dp.message_handler(Text('Создать объявление'))
async def make_announce(message: types.Message, state: FSMContext):
    if message.text == 'Отмена':
        await message.answer('Процесс отменен', reply_markup=kb_admin)
        return
    with connection.cursor() as cursor:
        cursor.execute("SELECT group_id from assistants WHERE assistant_id =" + "'" + str(message.from_user.id) + "';")
        group_names = list(cursor.fetchall())
    if not group_names:
        await message.reply('Вы не ассистент', reply_markup=kb_admin)
    else:
        async with state.proxy() as data:
            data['group_names'] = [item[0] for item in group_names]
        await message.reply('Выберите группу, которой нужно сделать объявление',
                            reply_markup=get_kb_buttons(group_names))
        await FSMAnnounce.group_id.set()



@dp.message_handler(state=FSMAnnounce.group_id)
async def get_subject(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        group_names = data['group_names']
    if message.text == 'Отмена':
        await message.answer('Процесс отменен', reply_markup=kb_admin)
        await state.finish()
    elif message.text not in group_names:
        await message.answer('Вы не являетесь ассистентом этой группы', reply_markup=kb_admin)
        await state.finish()
    else:
        with connection.cursor() as cursor:
            cursor.execute("SELECT subject_name from assistants WHERE assistant_id =" + "'" + str(message.from_user.id) + "' " + "AND group_id=" + "'" + message.text + "';")
            subject_names = list(cursor.fetchall())

        async with state.proxy() as data:
            data['subject_names'] = [item[0] for item in subject_names]
            data['selected_group'] = message.text

        await message.reply('Выберите предмет, по которому надо сделать объявление', reply_markup=get_kb_buttons(subject_names))
        await FSMAnnounce.next()


@dp.message_handler(state=FSMAnnounce.subject)
async def get_message(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        subject_names = data['subject_names']
    if message.text == 'Отмена':
        await message.answer('Процесс отменен', reply_markup=kb_admin)
        await state.finish()
    elif message.text not in subject_names:
        await message.answer('Вы не являетесь ассистентом этого предмета', reply_markup=kb_admin)
        await state.finish()
    else:
        await message.reply('Напишите объявление', reply_markup=kb_cancel)
        async with state.proxy() as data:
            data['selected_subject'] = message.text
        await FSMAnnounce.next()


@dp.message_handler(state=FSMAnnounce.announce)
async def get_message(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        selected_group = data['selected_group']
        selected_subject = data['selected_subject']

    if message.text == 'Отмена':
        await message.answer('Процесс отменен', reply_markup=kb_admin)
        await state.finish()
    else:
        with connection.cursor() as cursor:
            cursor.execute("SELECT student_id from groups WHERE group_id =" + "'" + selected_group + "';")
            for student in list(cursor.fetchall()):
                try:
                    await bot.send_message(chat_id=int(student[0]), text=f'#{selected_subject}\n'+message.text)
                except:
                    pass
        await message.answer('Объявление отправлено', reply_markup=kb_admin)
        await state.finish()


