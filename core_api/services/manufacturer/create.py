from django import forms
from rest_framework import status

from utils.services import ServiceWithResult
from models_app.models import Manufacturer


class CreateManufactureService(ServiceWithResult):
    name = forms.CharField(required=True)


    def process(self):
        if self.is_valid():
            self.result = self._create_manufacturer
            self.response_status = status.HTTP_201_CREATED
        return self

    @property
    def _create_manufacturer(self) -> Manufacturer:
        return Manufacturer.objects.create(name=self.cleaned_data['name'])
