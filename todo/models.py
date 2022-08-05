from django.db import models


class Task(models.Model):
    content = models.CharField(max_length=500)
    details = models.TextField(null=True)
    is_completed = models.BooleanField(default=False)
    is_subtask = models.BooleanField(default=False)
    completion_date = models.DateField(null=True)


class SubTasks(models.Model):
    task = models.ForeignKey(Task, related_name='main_task', on_delete=models.CASCADE)
    sub_tasks = models.ForeignKey(Task, unique=True, related_name='sub_task', on_delete=models.CASCADE)


class Todo(models.Model):
    title = models.CharField(max_length=100)
    task = models.ForeignKey(Task, related_name='todo', on_delete=models.CASCADE)


