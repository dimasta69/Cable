import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

celery_config = {
    'broker_url': os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    'result_backend': os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
    'accept_content': ['json'],
    'task_serializer': 'json',
    'result_serializer': 'json',
    'timezone': os.getenv('TIMEZONE', 'Europe/Moscow'),
    'beat_schedule': {
        'add-ten-minutes-every-10-minutes': {
            'task': 'license_api.tasks.add_ten_minutes',
            'schedule': int(os.getenv("LICENSE_CHECK_TIME_SECONDS", 600)),
        },
    }
}

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cabel.settings')

app = Celery('cabel')

app.config_from_object(celery_config)

app.autodiscover_tasks()
