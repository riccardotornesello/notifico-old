import os
from celery import Celery
from celery.schedules import crontab
from .tasks import checker

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notifico.settings')

app = Celery('notifico')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(crontab(minute='*'), checker.s('1m'), expires=10)
    sender.add_periodic_task(crontab(minute='*/5'), checker.s('5m'), expires=10)
    sender.add_periodic_task(crontab(minute='0'), checker.s('1h'), expires=10)
