from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery


def btnTask(task_id):
    return InlineKeyboardMarkup().add(
        KeyboardButton(text="Удалить", callback_data=f"delete{task_id}")
    )