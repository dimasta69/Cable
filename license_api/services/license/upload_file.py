import os
from rest_framework.exceptions import PermissionDenied
from rest_framework import status
import shutil

from django.forms import FileField
from utils.services import ServiceWithResult
from utils.fields import ModelField
from models_app.models import User
from cabel.settings.django import BASE_DIR


def move_past_file(license_dir_path, past_license_dir_path) -> None:
    if not os.path.exists(license_dir_path):
        past_license_dir_path.mkdir(parents=True, exist_ok=True)

    if license_dir_path.exists():
        for file_path in license_dir_path.iterdir():
            if file_path.is_file():
                shutil.move(str(file_path), str(past_license_dir_path / file_path.name))


class UploadFileService(ServiceWithResult):
    current_user = ModelField(User)
    uploaded_file = FileField()
    custom_validations = ['is_superuser', ]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.upload_file()
            self.response_status = status.HTTP_200_OK
        return self

    def upload_file(self) -> None:
        license_dir_path = BASE_DIR.parent / "license_api" / "license"
        past_license_dir_path = BASE_DIR.parent / "license_api" / "past_license"

        if not os.path.exists(past_license_dir_path):
            past_license_dir_path.mkdir(parents=True, exist_ok=True)

        move_past_file(license_dir_path, past_license_dir_path)

        uploaded_file = self.cleaned_data['uploaded_file']

        new_file_path = license_dir_path / uploaded_file.name

        with open(new_file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

    def is_superuser(self) -> None:
        if not self.cleaned_data['current_user'].is_superuser:
            self.add_error(
                "current_user",
                PermissionDenied(f"User id={self.cleaned_data['current_user'].id} is not superuser")
            )
            self.response_status = status.HTTP_403_FORBIDDEN
