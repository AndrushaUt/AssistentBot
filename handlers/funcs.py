from datetime import datetime
from create_bot import connection


def DeleteOldDead(name_table: str, student_name: str) -> list:
    output = []
    with connection.cursor() as cursor:
        if name_table == 'personal_deadlines':
            current_time = datetime.now()
            cursor.execute(
                f"SELECT * from personal_deadlines WHERE deadline_end_time <= '{current_time}' AND student_name = '{student_name}' ;"
            )
            output = cursor.fetchall()
            cursor.execute(
                f"DELETE from personal_deadlines WHERE deadline_end_time <= '{current_time}' AND student_name = '{student_name}' ;"
            )
            cursor.execute(
                f"DELETE from personal_deadlines WHERE is_done = TRUE AND student_name = '{student_name}' ;"
            )
    return output


def GetDeadlines(student_name: str):
    output = []
    with connection.cursor() as cursor:
        current_time = datetime.now()
        cursor.execute(
            f"SELECT * from personal_deadlines WHERE deadline_end_time > '{current_time}' AND student_name = '{student_name}' ;"
        )
        output = cursor.fetchall()
    return output


def OutputDeadlines(deleted_deadlines: list, title: str, text_end:str) -> str:
    output = f'{title}\n'
    counter = 1
    for dead in deleted_deadlines:
        output += f"{counter}. {dead[1]} {text_end} в {dead[0].strftime('%d/%m/%Y')}\n"
    return output


def IsStudent(user_id: str) -> bool:
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT student_name from groups WHERE student_id =" + "'" + user_id + "';")
        student_name = cursor.fetchone()
        if student_name:
            return True
        return False