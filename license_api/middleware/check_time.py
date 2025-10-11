import datetime
import os

import requests
from dotenv import load_dotenv

load_dotenv()

start_date_time = None


class LicenseOnlineMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, get_response):
        global start_date_time
        if not start_date_time:
            start_date_time = self.__check_time

        difference = abs(datetime.datetime.now() - start_date_time)
        if difference > datetime.timedelta(hours=12):
            start_date_time = self.__check_time

    @property
    def __check_time(self):
        try:
            license_path_datetime = os.getenv("LICENSE_PATH_DATETIME")
            response = requests.get(license_path_datetime, params={"utc": ""})
            date_time_str = response.json()["date_time"]
            return date_time_str
        except requests.exceptions.RequestException as e:
            print(f"Произошла ошибка при запросе: {e}")
