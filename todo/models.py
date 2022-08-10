from django.db import models
from django.shortcuts import get_object_or_404

from accounts.models import User


class Todo(models.Model):
    title = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return "Todo: " + str(self.id) + ", Title: " + str(self.title)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title
        }

    def get_tasks_as_list(self):
        return list(self.tasks.order_by('id').values(
                'id', 'content', 'details', 'is_completed', 'is_subtask', 'completion_date'
            ))

    @classmethod
    def queryset_to_list_of_dict(cls, queryset):
        todos = []
        for todo in queryset:
            data = todo.to_dict()
            data['tasks'] = todo.get_tasks_as_list()
            todos.append(data)
        return todos


class Task(models.Model):
    content = models.CharField(max_length=500)
    details = models.TextField(null=True)
    is_completed = models.BooleanField(default=False)
    is_subtask = models.BooleanField(default=False)
    completion_date = models.DateField(null=True)
    todo = models.ForeignKey(Todo, related_name='tasks', on_delete=models.CASCADE)

    def __str__(self):
        return "Todo: " + str(self.todo.id) + ", Current-task: " + str(self.id)

    def to_dict(self):
        data = {
            'id': self.id,
            'content': self.content,
            'details': self.details,
            'is_completed': self.is_completed,
            'is_subtask': self.is_subtask,
            'completion_date': self.completion_date,
            'todo': self.todo.id,
        }
        if self.is_subtask:
            data['parent'] = self.parent_task.task.id
        else:
            data['sub-tasks'] = list(self.sub_tasks.values_list('sub_task_id', flat=True))
        return data

    @classmethod
    def queryset_to_list_of_dict(cls, queryset):
        return [task.to_dict() for task in queryset]

    @classmethod
    def fill_data_from_instance(cls, data, instance):
        data_dict = data.copy()
        data_dict['content'] = data.get('content', instance.content)
        data_dict['details'] = data.get('details', instance.details)
        data_dict['is_completed'] = data.get('is_completed', instance.is_completed)
        data_dict['is_subtask'] = instance.is_subtask
        data_dict['completion_date'] = data.get('completion_date', instance.completion_date)
        if data.get('todo', None):
            todo = get_object_or_404(Todo, id=data.get('todo'))
            data_dict['todo'] = todo
        else:
            data_dict['todo'] = instance.todo
        return data_dict


class SubTask(models.Model):
    task = models.ForeignKey(Task, related_name='sub_tasks', on_delete=models.CASCADE)
    sub_task = models.OneToOneField(Task, related_name='parent_task', on_delete=models.CASCADE)

    def __str__(self):
        return "Todo: " + str(self.task.todo.id) + ", Task: " + \
               str(self.task.id) + ", Sub-task: " + \
               str(self.sub_task.id)

    def to_dict(self):
        data = {
            'id': self.id,
            'parent task': self.task.id,
            'sub task': list(self.task.sub_tasks.values_list('sub_task_id', flat=True)),
        }
        return data

    @classmethod
    def queryset_to_list_of_dict(cls, queryset):
        return [sub_task.to_dict() for sub_task in queryset]

# 2 Aspects not covered:
    # 1: If task is sub-task of its own
    # 2: If "task" is "sub-task" and "sub-task" is "task"
