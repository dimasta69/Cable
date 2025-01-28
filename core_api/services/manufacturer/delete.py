from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from functools import lru_cache

from utils.services import ServiceWithResult
from django import forms

from models_app.models import Manufacturer


class ManufacturerDeleteService(ServiceWithResult):
    id = forms.IntegerField(required=True)

    custom_validations = ['manufacturer_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self._delete_manufacturer()
            self.response_status = status.HTTP_204_NO_CONTENT
        return self

    def _delete_manufacturer(self) -> None:
        self._manufacturer.delete()

    @property
    @lru_cache()
    def _manufacturer(self) -> Manufacturer | None:
        try:
            return Manufacturer.objects.get(id=self.cleaned_data['id'])
        except Manufacturer.DoesNotExist:
            return None

    def manufacturer_presence(self):
        if not self._manufacturer:
            self.add_error('id', ObjectDoesNotExist(f'Port template id={self.cleaned_data["id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND
