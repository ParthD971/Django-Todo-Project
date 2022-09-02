from django.db import models
from django.shortcuts import get_object_or_404

from accounts.models import User


class Todo(models.Model):
    title = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        data = {
            'Todo': self.id,
            'Title': self.title,
            'Owner': self.owner.email,

        }
        return " | ".join([k+": "+str(v) for k, v in data.items()])

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'owner': self.owner.email,
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
            data['tasks'] = Task.queryset_to_list_of_dict(queryset=todo.tasks.order_by('id'))
            todos.append(data)
        return todos

    @classmethod
    def delete_todo(cls, todo_id=None):
        todo = get_object_or_404(cls, id=int(todo_id))
        todo.delete()


class Task(models.Model):
    content = models.CharField(max_length=500)
    details = models.TextField(null=True)
    is_completed = models.BooleanField(default=False)
    is_subtask = models.BooleanField(default=False)
    completion_date = models.DateField(null=True)
    todo = models.ForeignKey(Todo, related_name='tasks', on_delete=models.CASCADE)
    # parent = models.ForeignKey("self", related_name='tasks', on_delete=models.SET_NULL, default=None, null=True)

    def __str__(self):
        data = {
            'Todo': self.todo.id,
            'Current-task': self.id,
            'is_subtask': self.is_subtask,
        }
        # if self.parent:
        #     data.update({'parent': self.parent.id})

        sub_tasks = list(self.sub_tasks.values_list('sub_task_id', flat=True))
        if sub_tasks:
            data.update({'sub_tasks': sub_tasks})

        return " | ".join([k + ": " + str(v) for k, v in data.items()])

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
    def fill_data_from_instance(cls, data, instance_id=None):
        instance = get_object_or_404(Task, id=instance_id)

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
        return data_dict, instance

    @classmethod
    def delete_task(cls, task_id=None):
        task = get_object_or_404(cls, id=int(task_id))
        task.delete()


class SubTask(models.Model):
    task = models.ForeignKey(Task, related_name='sub_tasks', on_delete=models.CASCADE)
    sub_task = models.OneToOneField(Task, related_name='parent_task', on_delete=models.CASCADE)

    def __str__(self):
        data = {
            'Todo': self.task.todo.id,
            'Task': self.task.id,
            'Sub-task': self.sub_task.id,
        }
        return " | ".join([k + ": " + str(v) for k, v in data.items()])

    def to_dict(self):
        data = {
            'id': self.id,
            'parent task': self.task.id,
            'sub task': list(self.task.sub_tasks.values_list('sub_task_id', flat=True)),
        }
        return data

    # @classmethod
    # def queryset_to_list_of_dict(cls, queryset):
    #     return [sub_task.to_dict() for sub_task in queryset]

# 2 Aspects not covered:
    # 1: If task is sub-task of its own
    # 2: If "task" is "sub-task" and "sub-task" is "task"
