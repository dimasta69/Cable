from datetime import timedelta
from license_api.middleware.check_time import start_date_time


def add_ten_minutes():
    start_date_time + timedelta(minutes=10)
