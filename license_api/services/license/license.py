import datetime
import json
import os

from rest_framework import status
from rest_framework.exceptions import PermissionDenied

from utils.license.license_manager import LicenseManager
from utils.services import ServiceWithResult
from utils.fields import ModelField
from models_app.models import User
from models_app import models
from utils.license.exception import LicenseNotFoundException
from cabel.settings.django import BASE_DIR


class CheckLicenseService(ServiceWithResult):
    current_user = ModelField(User)

    custom_validations = ['is_superuser', ]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.read_file()
            self.response_status = status.HTTP_200_OK
        return self

    def read_file(self) -> json:
        license_dir_path = BASE_DIR.parent / "license_api" / "license"
        if not os.path.exists(license_dir_path):
            license_dir_path.mkdir(parents=True, exist_ok=True)
            raise LicenseNotFoundException("Нет файлов в license")

        files = list(license_dir_path.glob("*.license"))
        files = [f for f in files if f.is_file()]

        if files:
            first_file = sorted(files)[0]

            with open(first_file, "r", encoding="utf-8") as file:
                content = file.read()
                return self.read_license(content)

        else:
            self.add_error(
                "current_user",
                f"Папка license_api пуста"
            )
            self.response_status = status.HTTP_404_NOT_FOUND

    def read_license(self, content) -> json:
        license_engine = LicenseManager()
        parameters = license_engine.get_license_info(content)

        if parameters['time_unlimited'] is None:
            end_date = datetime.datetime.strptime(parameters['period_end_date'], '%Y-%m-%d %H:%M:%S')
            now = datetime.datetime.now()

            if end_date <= now:
                parameters['time_remainder'] = "Истекла"
            else:
                total_days = (end_date - now).days
                months = total_days // 30
                days = total_days % 30

                if months > 0 and days > 0:
                    parameters['time_remainder'] = f"{months} месяцев, {days} дней"
                elif months > 0:
                    parameters['time_remainder'] = f"{months} месяцев"
                elif days > 0:
                    parameters['time_remainder'] = f"{days} дней"
                else:
                    parameters['time_remainder'] = "Менее дня"

        parameters['restriction_remainder'] = []
        for model_name, count in parameters['restrictions'].items():
            count_remainder = int(count) - getattr(models, model_name).objects.all().count()
            parameters['restriction_remainder'].append({model_name: str(count_remainder)})

        return parameters

    def is_superuser(self) -> None:
        if not self.cleaned_data['current_user'].is_superuser:
            self.add_error(
                "current_user",
                PermissionDenied(f"User id={self.cleaned_data['current_user'].id} is not superuser")
            )
            self.response_status = status.HTTP_403_FORBIDDEN
