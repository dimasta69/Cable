import datetime
import os
import requests
from dotenv import load_dotenv
from django.core.cache import cache

load_dotenv()


class LicenseOnlineMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_date_time = cache.get('start_date_time')

        if not start_date_time:
            start_date_time = self.__check_time()
            cache.set('start_date_time', start_date_time, timeout=None)

        if start_date_time:
            if isinstance(start_date_time, str):
                start_date_time = datetime.datetime.fromisoformat(start_date_time)

            difference = abs(datetime.datetime.now() - start_date_time)
            if difference > datetime.timedelta(hours=12):
                start_date_time = self.__check_time()
                cache.set('start_date_time', start_date_time, timeout=None)

        response = self.get_response(request)
        return response

    def __check_time(self):
        try:
            license_path_datetime = os.getenv("LICENSE_PATH_DATETIME")
            response = requests.get(license_path_datetime, params={"utc": ""})
            date_time_str = response.json()["date_time"]
            return datetime.datetime.fromisoformat(date_time_str.replace('Z', '+00:00'))
        except requests.exceptions.RequestException as e:
            print(f"Произошла ошибка при запросе: {e} ....удалить")
            return datetime.datetime.now()
