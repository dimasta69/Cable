from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist

from utils.services import ServiceWithResult
from django import forms
from functools import lru_cache

from models_app.models.manufacturer import Manufacturer


class ManufacturerUpdateService(ServiceWithResult):
    name = forms.CharField(required=True)
    id = forms.IntegerField(required=True)

    custom_validations = ['name_presence', 'manufacture_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._update_scheme()
            self.response_status = status.HTTP_200_OK
        return self

    def _update_scheme(self):
        manufacturer = self.manufacturer
        manufacturer.name = self.cleaned_data['name']
        manufacturer.save()
        return manufacturer

    @property
    @lru_cache()
    def manufacturer(self):
        try:
            return Manufacturer.objects.get(id=self.cleaned_data['id'])
        except Manufacturer.DoesNotExist:
            return None

    @property
    def manufacturer_list(self):
        try:
            return Manufacturer.objects.all()
        except Manufacturer.DoesNotExist:
            return Manufacturer.objects.none()

    def name_presence(self):
        if self.manufacturer:
            for scheme in self.manufacturer_list:
                if scheme.name.lower() == self.cleaned_data['name'].lower():
                    self.add_error('name', ValidationError("Name="
                                                           f"{self.cleaned_data['name']} already exists"))
                    self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def manufacture_presence(self):
        if not self.manufacturer:
            self.add_error('id', ObjectDoesNotExist(f'Manufacture id={self.cleaned_data["id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND
