from django import forms
from django.core.exceptions import ValidationError
from rest_framework import status

from utils.services import ServiceWithResult
from models_app.models.manufacturer import Manufacturer


class CreateManufactureService(ServiceWithResult):
    name = forms.CharField(required=True)

    custom_validations = ['name_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.create_manufacturer
            self.response_status = status.HTTP_201_CREATED
        return self

    @property
    def create_manufacturer(self):
        return Manufacturer.objects.create(name=self.cleaned_data['name'])

    @property
    def manufacture_list(self):
        try:
            return Manufacturer.objects.all()
        except Manufacturer.DoesNotExist:
            return None

    def name_presence(self):
        for port in self.manufacture_list:
            if port.name == self.cleaned_data['name']:
                self.add_error('name', ValidationError(f'Field with title={self.cleaned_data["name"]}'
                                                       ' already exists'))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY
