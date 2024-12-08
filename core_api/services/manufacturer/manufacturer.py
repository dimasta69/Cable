from django import forms
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from functools import lru_cache

from utils.services import ServiceWithResult
from models_app.models import Manufacturer


class ManufacturerService(ServiceWithResult):
    id = forms.IntegerField(required=True)

    custom_validations = ['manufacturer_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.manufacturer
            self.response_status = status.HTTP_200_OK
        return self

    @property
    @lru_cache()
    def manufacturer(self):
        try:
            return Manufacturer.objects.get(id=self.cleaned_data['id'])
        except Manufacturer.DoesNotExist:
            return None

    def manufacturer_presence(self):
        if not self.manufacturer:
            self.add_error('id',  ObjectDoesNotExist(f'Manufacturer id={self.cleaned_data["id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND
