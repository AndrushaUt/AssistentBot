import asyncio
from datetime import datetime
from create_bot import assistants, personal_deadlines, groups, subjects, db, \
    connection, bot
from sqlalchemy import and_
import json
import requests


def DeleteOldDead(student_name: str) -> list:
    current_time = datetime.now()
    select_old_deadlines = db.select([personal_deadlines]).where(
        and_(personal_deadlines.columns.deadline_end_time <= current_time,
             personal_deadlines.columns.student_name == student_name))
    output = connection.execute(select_old_deadlines).fetchall()
    delete_old_deadlines = db.delete(personal_deadlines).where(
        and_(personal_deadlines.columns.deadline_end_time <= current_time,
             personal_deadlines.columns.student_name == student_name))
    connection.execute(delete_old_deadlines)
    delete_done_deadlines = db.delete(personal_deadlines).where(
        and_(personal_deadlines.columns.is_done == True,
             personal_deadlines.columns.student_name == student_name))
    connection.execute(delete_done_deadlines)
    return output


def GetDeadlines(student_name: str) -> list:
    current_time = datetime.now()
    get_actual_deadlines = db.select(personal_deadlines).where(
        and_(personal_deadlines.columns.deadline_end_time > current_time,
             personal_deadlines.columns.student_name == student_name))
    output = connection.execute(get_actual_deadlines).fetchall()
    return output


def OutputDeadlines(deleted_deadlines: list, title: str, text_end: str) -> str:
    output = f'{title}\n'
    counter = 1
    for dead in deleted_deadlines:
        output += f"{counter}. {dead[1]} {text_end} в {dead[0].strftime('%d/%m/%Y')}\n"
        counter+=1
    return output


def IsStudent(user_id: str) -> bool:
    get_curr_student = db.select(groups).where(
        groups.columns.student_id == user_id)
    student = connection.execute(get_curr_student).fetchone()
    if student:
        return True
    return False


def GetStudentName(user_id: str) -> str:
    get_student_name = db.select(groups.columns.student_name).where(
        groups.columns.student_id == user_id)
    student_name = connection.execute(get_student_name).fetchone()
    if student_name is None:
        return ""
    return student_name


def GetGroup(user_id: str) -> str:
    get_group_id = db.select(groups.columns.group_id).where(
        groups.columns.student_id == user_id)
    group = connection.execute(get_group_id).fetchone()
    return group[0]


def GetSubjectId(group_id: str) -> list:
    get_subject_id = db.select(subjects.columns.subject_id).where(
        subjects.columns.group_id == group_id)
    subject_id = connection.execute(get_subject_id).fetchall()
    if len(subject_id) == 0:
        return []
    return subject_id


def GetTableName(group_id: str, subject_id: str) -> list:
    get_table_name = db.select(subjects.columns.table_name).where(
        and_(subjects.columns.group_id == group_id,
             subjects.columns.subject_id == subject_id))
    table_name = connection.execute(get_table_name).fetchall()
    if len(table_name) == 0:
        return []
    return table_name


def GetTableHref(group_id: str, subject_id: str, table_name: str) -> list:
    get_table_href = db.select(subjects.columns.table_href).where(
        and_(subjects.columns.group_id == group_id,
             subjects.columns.subject_id == subject_id,
             subjects.columns.table_name == table_name))
    table_href = connection.execute(get_table_href).fetchall()
    if len(table_href) == 0:
        return []
    return table_href


def AddDeadline(date_end: datetime, subject_id: str, user_id: str,
                content: str):
    insertion_query = personal_deadlines.insert().values([
        {"deadline_end_time": date_end, "subject_name": subject_id,
         "student_name": user_id, "deadline_content": content}
    ])
    connection.execute(insertion_query)


def DeleteDeadline(date, student_id: str, subject_name: str, content: str):
    delete_q = db.delete(personal_deadlines).where(
        and_(personal_deadlines.columns.deadline_end_time == date,
             personal_deadlines.columns.student_name == student_id,
             personal_deadlines.columns.subject_name == subject_name,
             personal_deadlines.columns.deadline_content == content))
    connection.execute(delete_q)


async def AnnounceAboutDeadlineAndLesson(wait_for):
    get_all_id = connection.execute(
        db.select(groups.columns.student_id)).fetchall()
    while True:
        for idi in get_all_id:
            deadlines = GetDeadlines(str(idi[0]))
            deadlines_with_day_end = []
            for deadline in deadlines:
                if (deadline[0] - datetime.now()).days == 0 and deadline[
                    5] == False:
                    deadlines_with_day_end.append(deadline)
            if len(deadlines_with_day_end) != 0:
                m = OutputDeadlines(deadlines_with_day_end, "Внимание",
                                    "закончится сегодня, а именно")
                await bot.send_message(chat_id=int(idi[0]), text=m)
                for deadline in deadlines_with_day_end:
                    connection.execute(
                        db.update(personal_deadlines).where(and_(
                            personal_deadlines.columns.deadline_end_time ==
                            deadline[0],
                            personal_deadlines.columns.subject_name ==
                            deadline[1],
                            personal_deadlines.columns.student_name ==
                            deadline[2],
                            personal_deadlines.columns.deadline_content ==
                            deadline[3]
                        )).values(is_announced=True))

        for student_id, student_name in select_all_from_groups():
            time = datetime.now().strftime("%Y.%m.%d")
            r = requests.get(
                f'https://ruz.hse.ru/api/search?term={student_name}&type=student')
            page = r.content.decode("utf-8")

            id = json.loads(page)[0]['id']
            r = requests.get(
                f'https://ruz.hse.ru/api/schedule/student/{id}?start={time}&finish={time}&lng=2')
            page = r.content.decode("utf-8")

            for lesson in json.loads(page):
                str_time = datetime.now().strftime('%H:%M')
                time1 = datetime.strptime(str_time, '%H:%M')

                time2 = datetime.strptime(lesson["beginLesson"], '%H:%M')

                if 15 <= time2.hour * 60 + time2.minute - time1.hour * 60 + time1.minute < 30:
                    place = ''
                    if lesson["url1"] not in ['', None]:
                        place += f'<b>Online:</b> {lesson["url1"]}\n'
                    if lesson["auditorium"] not in ['', 'online', None]:
                        place += f'<b>Аудитория:</b> {lesson["auditorium"]}\n'
                    result = f'<b>Date:</b> {lesson["dayOfWeekString"]} {lesson["date"]} <u>{lesson["beginLesson"]}-{lesson["endLesson"]}</u>\n' \
                             f'<b>{lesson["kindOfWork"]}:</b> {lesson["discipline"]}\n' \
                             f'<b>Преподаватель:</b> {lesson["lecturer_title"]}\n' \
                             f'{place}\n'
                    await bot.send_message(chat_id=int(student_id),
                                           text=result, parse_mode='HTML')
        await asyncio.sleep(wait_for)


def select_assistant_id_from_assistants(query):
    row = db.select([assistants]).where(
        assistants.columns.assistant_id == query)
    if not connection.execute(row).fetchone():
        return None
    return connection.execute(row).fetchone()


def select_group_id_from_assistants(query):
    row = db.select([assistants]).where(
        assistants.columns.assistant_id == query)
    if not connection.execute(row).fetchall():
        return None
    return [(item[3],) for item in connection.execute(row).fetchall()]


def select_student_id_from_groups_by_group_id(query):
    row = db.select([groups]).where(groups.columns.group_id == query)
    if not connection.execute(row).fetchall():
        return []
    return [(item[0],) for item in connection.execute(row).fetchall()]


def get_subjects(query1, query2):
    row = db.select([assistants]).where(
        (assistants.columns.assistant_id == query1) & (
                assistants.columns.group_id == query2))
    if not connection.execute(row).fetchall():
        return None
    return [(item[2],) for item in connection.execute(row).fetchall()]


def insert_into_subjects(values):
    insertion = subjects.insert().values([
        dict(zip(['assistant_id', 'group_id', 'subject_id', 'table_name',
                  'table_href'], values))
    ])
    connection.execute(insertion)


def select_all_from_groups():
    row = db.select([groups])
    if not connection.execute(row).fetchall():
        return None
    return [(item[0], item[1]) for item in connection.execute(row).fetchall()]
