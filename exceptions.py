class NotCorrectMessage(Exception):
    """Ошибка в распарсе сообщения"""
    pass


class TaskNotExist(Exception):
    """Напоминание не существует"""
    pass


class TasksListIsEmpty(Exception):
    """Список напоминаний пуст"""
    pass

class TaskOwnerIsDifferent(Exception):
    """Напоминание принадлежит другому пользователю"""
    pass