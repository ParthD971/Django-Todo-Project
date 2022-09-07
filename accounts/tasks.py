# todo/tasks.py

from celery import shared_task
from django.core.mail import EmailMessage
import logging

logger = logging.getLogger('accounts')

@shared_task()
def send_mail_task(subject, html_content, to):
    msg = EmailMessage(subject, html_content, to=[to])
    msg.send()
    logger.info(f'Celary task(send_mail_task): Email set to {to} successfully.')

