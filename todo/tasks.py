# todo/tasks.py
from datetime import datetime

from celery import shared_task

from django.utils.translation import gettext_lazy as _

from accounts.utils import send_mail
from .models import Task


@shared_task
def send_reminder_mail():
    queryset = Task.objects.filter(completion_date=datetime.today().date())
    print(queryset)
    for obj in queryset:
        context = {
            'subject': _('Task reminder'),
            'task_content': obj.content,
            'task_completion_date': obj.completion_date,
            'task_todo_title': obj.todo.title,
        }
        send_mail(obj.todo.owner.email, 'task_reminder', context)


