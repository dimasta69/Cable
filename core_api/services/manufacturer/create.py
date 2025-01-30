from django import forms
from rest_framework import status
from rest_framework.exceptions import PermissionDenied

from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models import Manufacturer, User


class CreateManufactureService(ServiceWithResult):
    name = forms.CharField(required=True)
    current_user = ModelField(User)

    custom_validations = ['is_superuser']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._create_manufacturer
            self.response_status = status.HTTP_201_CREATED
        return self

    @property
    def _create_manufacturer(self) -> Manufacturer:
        return Manufacturer.objects.create(name=self.cleaned_data['name'])

    def is_superuser(self) -> None:
        if not self.cleaned_data['current_user'].is_superuser:
            self.add_error(
                "current_user",
                PermissionDenied(
                    "User is not superuser"
                )
            )
