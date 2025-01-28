from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist

from utils.services import ServiceWithResult
from django import forms
from functools import lru_cache

from models_app.models import Manufacturer


class ManufacturerUpdateService(ServiceWithResult):
    name = forms.CharField(required=True)
    id = forms.IntegerField(required=True)

    custom_validations = ['name_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._update_scheme()
            self.response_status = status.HTTP_200_OK
        return self

    def _update_scheme(self) -> Manufacturer:
        manufacturer = self._manufacturer
        manufacturer.name = self.cleaned_data['name']
        manufacturer.save()
        return manufacturer

    @property
    @lru_cache()
    def _manufacturer(self) -> Manufacturer | None:
        try:
            return Manufacturer.objects.get(id=self.cleaned_data['id'])
        except Manufacturer.DoesNotExist:
            return None

    def manufacture_presence(self) -> None:
        if not self._manufacturer:
            self.add_error('id', ObjectDoesNotExist(f'Manufacture id={self.cleaned_data["id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND
