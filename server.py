
import datetime
import sys, os

import local_settings as settings
import notifications as notify
import exceptions
import keyboard


try:
    import aiogram
    from aiogram import Bot, Dispatcher, executor, types
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
except Exception as e:
    print(e)
    os.system('pip install aiogram & pip install apscheduler')
    sys.exit("Restart the script.")


api = Bot(token = settings.TOKEN, parse_mode=types.ParseMode.MARKDOWN)
dp = Dispatcher(api)
sch = AsyncIOScheduler()
sch.configure(timezone="Europe/Kiev")


@dp.callback_query_handler(lambda x: x.data.startswith('delete'))
async def deleteTask(callback_query: types.CallbackQuery) -> None:
    """Удаление напоминания"""
    await api.answer_callback_query(callback_query.id)
    task_id = int(callback_query.data.split('delete')[1])
    notify.delete_task(task_id)
    await api.send_message(callback_query.message.chat.id, "Напоминание удалено")
    await api.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    await send_reminder()
     

@dp.message_handler(commands=['start'])
async def start(message: types.Message) -> None:
    """Приветсвие и помощь по боту"""
    await message.reply(
"""Привет,
Я бот для напоминаний.
Если написать мне напоминание по формату:
ДД.ММ.ГГГГ ЧЧ:ММ:СС Текст напоминания
То я буду напоминать в указанное время.
Часть даты может быть оставлена пустой.
Тогда будет использоваться текущая дата.

Чтобы посмотреть список напоминаний, напишите мне /myTasks.""")


@dp.message_handler(commands=['myTasks'])
async def myTasks(message: types.Message) -> None:
    """Посмотреть свои напоминания"""
    tasks = notify.get_tasks(message.from_user.id)
    await message.reply(tasks)
    


@dp.message_handler(regexp="/(task)+([0-9])+")
async def show_task(message:types.Message) -> None:
    """Показывает напоминание"""
    task_id = message.get_command().split("/task")[1]
    try:
        task = notify.get_task(message.from_user.id, task_id)

    except exceptions.TaskNotExist:
        await message.reply("Напоминание не существует или было удалено")
        return

    except exceptions.TaskOwnerIsDifferent:
        await message.reply("Напоминание принадлежит другому пользователю")
        return

    await message.reply(task, reply_markup=keyboard.btnTask(task_id))

         

@dp.message_handler()
async def add_task(message: types.Message) -> None:
    """Добавить новое напоминание"""

    try:

        await message.reply(notify.add_task(message))
        await send_reminder()
        
    except exceptions.NotCorrectMessage as e:
        await message.reply(e)
        return

    except AttributeError as e:
        print(e)
        


async def send_reminder() -> None:
    """Отправляет напоминание"""
    
    try:
        task = notify.findNearTask()
        if task.datetime <= datetime.datetime.now():
            await api.send_message(task.userid, task.text)
            print("Отправлено")
            notify.repeatOrNot(task)
            await send_reminder()

        else:
            print('Ждем')
            sch.add_job(send_reminder, 'date', run_date=task.datetime)
            try:
                sch.start(paused=False)
            except Exception as e:
                pass


    except aiogram.exceptions.ChatNotFound:
        notify.delete_task(task.id)
        await send_reminder()

    except exceptions.TasksListIsEmpty:
        try:
            sch.shutdown()
        except AttributeError:
            print("Нет задач. Шедулер остановлен")



if __name__ =="__main__":
    executor.start(dp, send_reminder())
    executor.start_polling(dp, skip_updates=True)