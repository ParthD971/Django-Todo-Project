# core/celery.py

import os
from celery import Celery
import dotenv

dotenv.load_dotenv()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
app = Celery("core")
app.conf.enable_utc = False
app.conf.update(timezone='Asia/Kolkata')

app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.beat_schedule = {
    # Schedulers
    'check_and_send_pending_mails': {
        'task': 'todo.tasks.send_reminder_mail',
        'schedule': int(os.environ.get('REMINDER_SCHEDULE_DURATION', '86400')),  # every 86400 seconds it will be called
        # 'args': (2,) you can pass arguments also if required
    }
}

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
