# todo/tasks.py

from celery import shared_task
from django.core.mail import EmailMessage


@shared_task()
def send_mail_task(subject, html_content, to):
    msg = EmailMessage(subject, html_content, to=[to])
    msg.send()

