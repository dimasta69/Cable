from utils.fields import ModelField
from utils.services import ServiceWithResult
from django.core.exceptions import ValidationError, PermissionDenied
from rest_framework import status

from django import forms
from models_app.models import TypePort, User


class CreateTypePort(ServiceWithResult):
    name = forms.CharField(required=True)
    current_user = ModelField(User)

    custom_validations = ['unique_type', 'is_superuser']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._create_type_port
        return self

    @property
    def _create_type_port(self) -> TypePort:
        return TypePort.objects.create(name=self.cleaned_data['name'])

    def unique_type(self) -> None:
        if self.cleaned_data['name'] and TypePort.objects.filter(name=self.cleaned_data['name']):
            self.add_error("name", ValidationError(f"Name = {self.cleaned_data['name']} is not unique"))
            self.response_status = status.HTTP_400_BAD_REQUEST

    def is_superuser(self) -> None:
        if not self.cleaned_data['current_user'].is_superuser:
            self.add_error(
                "current_user",
                PermissionDenied(
                    "User is not superuser"
                )
            )
