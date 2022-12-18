from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types
from create_bot import dp
from keyboards.client_kb import kb_client, create_kb_buttons, \
    kb_deadlines_client, kb_timetable_client
from keyboards.start_kb import kb_start
from handlers.funcs import *
import requests
import json


class FSMSubject(StatesGroup):
    subject_name = State()
    tables_name = State()


class FSMDeadline(StatesGroup):
    funct_choice = State()
    subject_name = State()
    content = State()
    time_end = State()
    deadline_choice = State()


class FSMTimetable(StatesGroup):
    format = State()


@dp.message_handler(Text("Студент"))
async def cm(message: types.Message):
    student_name = GetStudentName(str(message.from_user.id))
    if student_name:
        await message.answer(
            f"Вход выполнен...\nДобро пожаловать, {student_name[0]}",
            reply_markup=kb_client)
    else:
        await message.answer("Вы не являетесь студентом ВШЭ",
                             reply_markup=kb_start)


@dp.message_handler(Text("Получить оценку"), state=None)
async def get_mark(message: types.Message, state: FSMContext):
    if IsStudent(str(message.from_user.id)):
        group_name = GetGroup(str(message.from_user.id))
        temp_cursor = GetSubjectId(group_name)
        if len(temp_cursor) == 0:
            await message.answer("Пока никаких предметов не добавлено",
                                 reply_markup=kb_client)
        else:
            await message.answer("Выберите предмет",
                                 reply_markup=create_kb_buttons(
                                     list(temp_cursor)))
            await FSMSubject.subject_name.set()
            async with state.proxy() as data:
                data["group_name"] = group_name
    else:
        await message.answer("Не пытайтесь хакнуть нашего бота",
                             reply_markup=kb_start)


@dp.message_handler(state=FSMSubject.subject_name)
async def get_subject(message: types.Message, state: FSMContext):
    if message.text == 'Отмена':
        await state.finish()
        await message.answer("Процесс отменен",
                             reply_markup=kb_client)
        return
    async with state.proxy() as data:
        data['current_subject'] = message.text
        temp_cursor = GetTableName(data['group_name'], data['current_subject'])
        if len(temp_cursor) == 0:
            await message.answer("Пока никакие таблицы не добавлены",
                                 reply_markup=kb_client)
        else:
            await message.answer("Выберите название таблицы",
                                 reply_markup=create_kb_buttons(
                                     list(temp_cursor)))
            await FSMSubject.next()


@dp.message_handler(state=FSMSubject.tables_name)
async def get_subject(message: types.Message, state: FSMContext):
    if message.text == 'Отмена':
        await state.finish()
        await message.answer("Процесс отменен",
                             reply_markup=kb_client)
        return
    async with state.proxy() as data:
        temp_cursor = GetTableHref(data["group_name"], data['current_subject'],
                                   message.text)
        if len(temp_cursor) == 0:
            await message.answer("Пока никакие таблицы не добавлены",
                                 reply_markup=kb_client)
        else:
            await message.answer(temp_cursor[0][0],
                                 reply_markup=kb_client)
    await state.finish()


@dp.message_handler(Text("Получить дедлайны"), state=FSMDeadline.funct_choice)
async def get_deadlines(message: types.Message, state: FSMContext):
    await state.finish()
    deleted_deadlines = DeleteOldDead(str(message.from_user.id))
    if len(deleted_deadlines) != 0:
        await message.answer(
            OutputDeadlines(deleted_deadlines, 'Прошедшие дедлайны',
                            'закончился'))
    current_deadlines = GetDeadlines(str(message.from_user.id))
    if len(current_deadlines) != 0:
        await message.answer(
            OutputDeadlines(current_deadlines, 'Актуальные дедлайны',
                            'закончится'))
        await message.answer('Что хотите сделать?', reply_markup=kb_client)
    else:
        await message.answer(
            'Пока нету актуальных дедлайнов\n Но вы можете их добавить,'
            'чтобы ничего не забыть!', reply_markup=kb_client)


@dp.message_handler(Text("Дедлайны"))
async def get_deadlines(message: types.Message):
    if IsStudent(str(message.from_user.id)):
        await FSMDeadline.funct_choice.set()
        await message.answer("Что вы хотите сделать с вашими делайнами",
                             reply_markup=kb_deadlines_client)
    else:
        await message.answer("Не пытайтесь хакнуть нашего бота",
                             reply_markup=kb_start)


@dp.message_handler(Text("Отмена"), state=FSMDeadline.funct_choice)
async def cancel_deadline_choice(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Процесс отменен", reply_markup=kb_client)
    return


@dp.message_handler(Text("Создать свой дедлайн"),
                    state=FSMDeadline.funct_choice)
async def WriteSubjectName(message: types.Message):
    await message.answer("Напишите название предмета")
    await FSMDeadline.next()


@dp.message_handler(state=FSMDeadline.subject_name)
async def WriteDeadlineContent(message: types.Message, state: FSMContext):
    if message.text.lower() == 'отмена':
        await state.finish()
        await message.answer("Процесс отменен", reply_markup=kb_client)
        return
    async with state.proxy() as data:
        data['subject_name'] = message.text
    await message.answer("Напишите содержание вашего дедлайна")
    await FSMDeadline.next()


@dp.message_handler(state=FSMDeadline.content)
async def WriteEndTime(message: types.Message, state: FSMContext):
    if message.text.lower() == 'отмена':
        await state.finish()
        await message.answer("Процесс отменен", reply_markup=kb_client)
        return
    async with state.proxy() as data:
        data['content'] = message.text
    await message.answer("Напишите время окончания вашего дедлайна\n"
                         "Формат даты DD-MM-YYYY")
    await FSMDeadline.next()


@dp.message_handler(state=FSMDeadline.time_end)
async def WriteEndTime(message: types.Message, state: FSMContext):
    if message.text.lower() == 'отмена':
        await state.finish()
        await message.answer("Процесс отменен", reply_markup=kb_client)
        return
    date: datetime
    try:
        date = datetime.strptime(message.text, "%d-%m-%Y")
        async with state.proxy() as data:
            AddDeadline(date, data['subject_name'], str(message.from_user.id),
                        data['content'])
        await message.answer("Дедлайн успешно добавлен")
        await message.answer('Что хотите сделать?', reply_markup=kb_client)
        await state.finish()
    except ValueError:
        await message.answer(
            "Вы ввели неверный формат даты, попробуйте еще раз или напишите 'отмена'")
        return


@dp.message_handler(Text("Отметить дедлайн"), state=FSMDeadline.funct_choice)
async def ChooseDeadline(message: types.Message, state: FSMContext):
    if message.text.lower() == 'отмена':
        await state.finish()
        await message.answer("Процесс отменен", reply_markup=kb_client)
        return
    DeleteOldDead(str(message.from_user.id))
    await FSMDeadline.deadline_choice.set()
    output = GetDeadlines(str(message.from_user.id))
    if len(output) == 0:
        await message.answer(
            'Пока нету актуальных дедлайнов\n Но вы можете их добавить,'
            'чтобы ничего не забыть!', reply_markup=kb_client)
        await state.finish()
        return
    await message.answer(
        OutputDeadlines(output, 'Актуальные дедлайны',
                        'закончится'))
    await message.answer(
        "Напишите номера через пробел дедлайнов, которые хотите отметить сделанными")


@dp.message_handler(state=FSMDeadline.deadline_choice)
async def TagDeadlines(message: types.Message, state: FSMContext):
    if message.text.lower() == 'отмена':
        await state.finish()
        await message.answer("Процесс отменен", reply_markup=kb_client)
        return
    numbers: list
    try:
        numbers = list(map(int, message.text.split()))
    except ValueError:
        await message.answer(
            "Вы ввели неверный формат номеров, попробуйте еще раз или напишите 'отмена'")
        return
    deadlines = GetDeadlines(str(message.from_user.id))
    for num in numbers:
        if num - 1 < len(deadlines):
            deadline = deadlines[num - 1]
            DeleteDeadline(deadline[0], deadline[2], deadline[1], deadline[3])
    await state.finish()
    await message.answer(
        "Выбранные вами дедлайны успешно отмечены сделанными\n")
    await message.answer('Что хотите сделать?', reply_markup=kb_client)


@dp.message_handler(Text("Сегодня"), state=FSMTimetable.format)
async def get_schedule_today(message: types.Message, state: FSMContext):
    student_name = GetStudentName(str(message.from_user.id))
    req = student_name[0]
    time = datetime.now().strftime("%Y.%m.%d")
    r = requests.get(f'https://ruz.hse.ru/api/search?term={req}&type=student')
    page = r.content.decode("utf-8")

    id = json.loads(page)[0]['id']
    r = requests.get(
        f'https://ruz.hse.ru/api/schedule/student/{id}?start={time}&finish={time}&lng=2')
    page = r.content.decode("utf-8")
    mes = ''
    for lesson in json.loads(page):
        place = ''
        if lesson["url1"] not in ['', None]:
            place += f'<b>Online:</b> {lesson["url1"]}\n'
        if lesson["auditorium"] not in ['', 'online', None]:
            place += f'<b>Аудитория:</b> {lesson["auditorium"]}\n'
        result = f'<b>Date:</b> {lesson["dayOfWeekString"]} {lesson["date"]} <u>{lesson["beginLesson"]}-{lesson["endLesson"]}</u>\n' \
                 f'<b>{lesson["kindOfWork"]}:</b> {lesson["discipline"]}\n' \
                 f'<b>Преподаватель:</b> {lesson["lecturer_title"]}\n' \
                 f'{place}\n'

        mes += result
    await state.finish()
    if mes == "":
        await message.answer("Сегодня пар нету, отдыхай!", reply_markup=kb_client, parse_mode="HTML")
    else:
        await message.answer(mes, reply_markup=kb_client, parse_mode="HTML")


@dp.message_handler(Text("Неделя"), state=FSMTimetable.format)
async def get_schedule_today(message: types.Message, state: FSMContext):
    student_name = GetStudentName(str(message.from_user.id))
    req = student_name[0]
    days = datetime.toordinal(datetime.now())
    weekday = datetime.weekday(datetime.now())
    start = datetime.fromordinal(days - weekday).strftime("%Y.%m.%d")
    finish = datetime.fromordinal(days - weekday + 6).strftime("%Y.%m.%d")

    r = requests.get(f'https://ruz.hse.ru/api/search?term={req}&type=student')
    page = r.content.decode("utf-8")
    id = json.loads(page)[0]['id']

    r = requests.get(
        f'https://ruz.hse.ru/api/schedule/student/{id}?start={start}&finish={finish}&lng=2')
    page = r.content.decode("utf-8")
    mes = ''
    for lesson in json.loads(page):
        place = ''
        if lesson["url1"] not in ['', None]:
            place += f'<b>Online:</b> {lesson["url1"]}\n'
        if lesson["auditorium"] not in ['', 'online', None]:
            place += f'<b>Аудитория:</b> {lesson["auditorium"]}\n'
        result = f'<b>Date:</b> {lesson["dayOfWeekString"]} {lesson["date"]} <u>{lesson["beginLesson"]}-{lesson["endLesson"]}</u>\n' \
                 f'<b>{lesson["kindOfWork"]}:</b> {lesson["discipline"]}\n' \
                 f'<b>Преподаватель:</b> {lesson["lecturer_title"]}\n' \
                 f'{place}\n'

        mes += result
    await state.finish()
    if mes == "":
        await message.answer("Сегодня пар нету, отдыхай!",
                             reply_markup=kb_client, parse_mode="HTML")
    else:
        await message.answer(mes, reply_markup=kb_client, parse_mode="HTML")


@dp.message_handler(Text("Расписание"))
async def choose_format(message: types.Message):
    if IsStudent(str(message.from_user.id)):
        await FSMTimetable.format.set()
        await message.answer("Выберете период",
                             reply_markup=kb_timetable_client)
    else:
        await message.answer("Не пытайтесь хакнуть нашего бота",
                             reply_markup=kb_start)


@dp.message_handler(Text("Отмена"), state=FSMTimetable.format)
async def cancel_deadline_choice(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Процесс отменен", reply_markup=kb_client)
    return
