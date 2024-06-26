from functools import lru_cache

from django import forms
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework import status

from utils.services import ServiceWithResult
from models_app.models.building import Building
from models_app.models.scheme import Scheme


class CreateBuildingService(ServiceWithResult):
    scheme_id = forms.IntegerField(required=True)
    number = forms.CharField(required=True)

    custom_validations = ['scheme_presence', 'number_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.create_building
            self.response_status = status.HTTP_201_CREATED
        return self

    @property
    def create_building(self):
        return Building.objects.create(scheme=self.scheme, number=self.cleaned_data['number'])

    @property
    @lru_cache()
    def scheme(self):
        try:
            return Scheme.objects.get(id=self.cleaned_data['scheme_id'])
        except Scheme.DoesNotExist:
            return None

    @property
    @lru_cache()
    def building_list(self):
        try:
            return Building.objects.filter(scheme=self.scheme)
        except Building.DoesNotExist:
            return Building.objects.none()

    def scheme_presence(self):
        if not self.scheme:
            self.add_error('scheme_id', ObjectDoesNotExist('Scheme id='
                                                           f'{self.cleaned_data["scheme_id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def number_presence(self):
        for building in self.building_list:
            if building.number.lower() == self.cleaned_data['number'].lower():
                self.add_error('number', ValidationError(f'Field with number={self.cleaned_data["number"]}'
                                                         ' already exists'))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY
