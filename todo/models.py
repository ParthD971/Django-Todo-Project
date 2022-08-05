from django.db import models


class Todo(models.Model):
    title = models.CharField(max_length=100)

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
        return {
            'id': self.id,
            'content': self.content,
            'details': self.details,
            'is_completed': self.is_completed,
            'is_subtask': self.is_subtask,
            'completion_date': self.completion_date,
            'todo': self.todo.id,
        }

    @classmethod
    def queryset_to_list_of_dict(cls, queryset):
        return [task.to_dict() for task in queryset]


class SubTask(models.Model):
    task = models.ForeignKey(Task, related_name='sub_tasks', on_delete=models.CASCADE)
    sub_task = models.OneToOneField(Task, related_name='parent_task', on_delete=models.CASCADE)

    def __str__(self):
        return "Task: " + str(self.task.id) + ", Sub-task: " + str(self.sub_task.id)

# 2 Aspects not covered:
    # 1: If task is sub-task of its own
    # 2: If "task" is "sub-task" and "sub-task" is "task"
