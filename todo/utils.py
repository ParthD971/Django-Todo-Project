from django.shortcuts import get_object_or_404

from todo.models import Todo


def get_dic(data, **kwargs):
    """
    Adds data to given data dictionary
    :param data: dict
    :param kwargs: dict to be added
    :return: new data
    """
    d = data.copy()
    for k, v in kwargs.items():
        d[k] = v
    return d


def check_and_get_todo(todo_id=None):
    """
    Checks for todo existence.
    :param todo_id: integer 'id' for todo
    :return: tuple (obj, bool)
    """
    if not todo_id or todo_id.strip() == '':
        return 0, 0
    todo = get_object_or_404(Todo, id=todo_id)
    return todo, 1
