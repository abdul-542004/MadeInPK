import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MadeInPK.settings')

app = Celery('MadeInPK')

# Load configuration from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()


# Periodic tasks
app.conf.beat_schedule = {
    'check-auction-endings': {
        'task': 'api.tasks.check_auction_endings',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    'check-payment-deadlines': {
        'task': 'api.tasks.check_payment_deadlines',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
    'send-pending-notifications': {
        'task': 'api.tasks.send_pending_notifications',
        'schedule': crontab(minute='*/10'),  # Every 10 minutes
    },
}


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
