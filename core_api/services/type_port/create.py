from utils.services import ServiceWithResult
from django.core.exceptions import ValidationError
from rest_framework import status

from django import forms
from models_app.models import TypePort


class CreateTypePort(ServiceWithResult):
    name = forms.CharField(required=True)

    custom_validations = ['unique_type',]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._create_type_port()
        return self

    def _create_type_port(self):
        return TypePort.objects.create(name=self.cleaned_data['name'])

    def unique_type(self):
        if self.cleaned_data['name'] and TypePort.objects.filter(name=self.cleaned_data['name']):
            self.add_error("name", ValidationError(f"Name = {self.cleaned_data['name']} is not unique"))
            self.response_status = status.HTTP_400_BAD_REQUEST
