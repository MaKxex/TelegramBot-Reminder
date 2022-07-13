from typing import NamedTuple
from aiogram import types
from parse import *
import datetime
import exceptions
import db
import re
from dateutil.relativedelta import relativedelta

class Message(NamedTuple):
    """Структура распаршенного сообщения о новом напоминании"""
    user_id: int
    datetime: datetime.datetime
    repeat_flag: bool
    text: str


def add_task(message: types.Message) -> str:
    """Парсинг сообщения и добавление напоминания в базу данных"""
    try:
        parsedMessage = _parsing_message(message)
    except exceptions.NotCorrectMessage as e:
        raise e
    try:
        db.add_task(parsedMessage)
    except Exception as e:
        print(e)
        return "Ошибка при добавлении напоминания"
    return "Ваше напоминание добавлено!"

def delete_task(TaskID: int) -> None:
    """Удаление напоминания"""
    db.delete_task(TaskID)


def changeTask(TaskID: int, **kwargs) -> None:
    """Изменение напоминания"""
    db.edit_task(TaskID, **kwargs)
    

def repeatOrNot(task: db.Task) -> None:
    """Проверка на повторение напоминания"""
    if task.repeat:
        print(1)
        print(task.datetime + relativedelta(days=+1))
        db.edit_task(task.id, datetime=task.datetime+relativedelta(days=+1))
        return
    
    db.delete_task(task.id)


def get_task(userid ,task_id: int) -> str:
    """Получение напоминания"""
    try:
        task = db.get_task(task_id)
    except exceptions.TaskNotExist:
        raise exceptions.TaskNotExist("Напоминание не существует или было удалено")
    
    if task.userid != userid:
        raise exceptions.TaskOwnerIsDifferent("Вы не владелец напоминания")

    return "Напоминание: {task_id},\nДата: {datetime},\nПовторять: {repeat},\n{text}".format(
        task_id=task.id,
        datetime=task.datetime,
        repeat="Да" if task.repeat else "Нет",
        text=task.text
    )


def get_tasks(userid: int) -> str:
    """Получение списка напоминаний"""
    tasks= db.get_tasks(userid)
    string = ""
    for task in tasks:
        string += "/task{task_id}, {datetime},\n{text}...\n\n".format(
            task_id=task.id,
            datetime=task.datetime,
            text=task.text[:20]
        )
    return string

def findNearTask() -> db.Task: 
    """Поиск ближайшего напоминания,
       возвращает обьект напоминания."""
    try: 
        return db.get_NearTask()
    except exceptions.TasksListIsEmpty:
        raise exceptions.TasksListIsEmpty


def _parsing_message(message: types.message) -> Message:
    """Парсинг сообщения приходящая от бота"""
    regexp_result = re.match("((?:0[1-9]|[12][0-9]|3[01])(?:|[-/.](?:0[1-9]|1[012]))(?:|[-/.](?:19\d{2}|20[01][0-9]|2022))|)(?:(?:|\s)([0-9]{2}:[0-9]{2}(?:|:[0-9]{2}(?:[0-9]{1,3})?)))((?: | пвт| rep)|) (.*)", message.text)
    if not regexp_result or not regexp_result.group(4):
        raise exceptions.NotCorrectMessage("Некорректное сообщение. Напишите в формате: \nДД/ММ/ГГГГ ЧЧ:ММ пвт напоминание.\nЧЧ:ММ напоминание")

    date = re.split("[-/.]", regexp_result.group(1))
    time = re.split(":", regexp_result.group(2))
    match date:
        case date if date[0] == "":
            datetim = datetime.datetime.now().replace(hour=int(time[0]), minute=int(time[1]), second=0, microsecond=0)
        case date if len(date) == 1:
            datetim = datetime.datetime.now().replace(day=int(date[0]), hour=int(time[0]), minute=int(time[1]), second=0, microsecond=0)
        case date if len(date) == 2:
            datetim = datetime.datetime.now().replace(day=int(date[0]), month=int(date[1]), hour=int(time[0]), minute=int(time[1]), second=0,microsecond=0)
        case date if len(date) == 3:
            datetim = datetime.datetime.strptime(f"{date[0]}/{date[1]}/{date[2]}","%d/%m/%Y").replace(hour=int(time[0]), minute=int(time[1]), second=0,microsecond=0)

    return Message(message.from_user.id,datetim, regexp_result.group(3).strip() == "rep" or regexp_result.group(3).strip() == "пвт", regexp_result.group(4))

    