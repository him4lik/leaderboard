import os
from celery import Celery, Task
from . import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'leaderboard.settings')

app = Celery('leaderboard')

app.conf.update(
    CELERY_ACCEPT_CONTENT=['json'],
    CELERY_TASK_SERIALIZER='json',
    CELERY_RESULT_SERIALIZER='json',
)
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.Task = Task