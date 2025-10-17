from django.core.cache import cache
import datetime

from dotenv import load_dotenv
import os
from celery import shared_task

load_dotenv()


@shared_task
def add_ten_minutes():
    start_date_time = cache.get('start_date_time')
    check_time_seconds = int(os.getenv("LICENSE_CHECK_TIME_SECONDS", 600))

    if start_date_time:
        if isinstance(start_date_time, str):
            start_date_time = datetime.datetime.fromisoformat(start_date_time)
        start_date_time += datetime.timedelta(seconds=check_time_seconds)
        cache.set('start_date_time', start_date_time, timeout=None)
    else:
        pass
