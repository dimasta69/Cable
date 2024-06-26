from functools import lru_cache

from django import forms
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework import status

from utils.services import ServiceWithResult
from models_app.models.building import Building


class UpdateBuildingService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    number = forms.CharField(required=False)
    coord_x = forms.FloatField(required=False)
    coord_y = forms.FloatField(required=False)

    custom_validations = ['building_presence', 'number_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.update_building
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def update_building(self):
        building = self.building
        if self.cleaned_data['number']:
            building.number = self.cleaned_data['number']
        if self.cleaned_data['coord_x']:
            building.coord_x = self.cleaned_data['coord_x']
        if self.cleaned_data['coord_y']:
            building.coord_y = self.cleaned_data['coord_y']
        building.save()
        return building

    @property
    @lru_cache()
    def building(self):
        try:
            return Building.objects.get(id=self.cleaned_data['id'])
        except Building.DoesNotExist:
            return None

    @property
    @lru_cache()
    def building_list(self):
        try:
            return Building.objects.filter(scheme=self.building.scheme)
        except Building.DoesNotExist:
            return Building.objects.none()

    def building_presence(self):
        if not self.building:
            self.add_error('id', ObjectDoesNotExist('Building id='
                                                    f'{self.cleaned_data["id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def number_presence(self):
        for building in self.building_list:
            if building.number.lower() == self.cleaned_data['number'].lower():
                self.add_error('number', ValidationError(f'Field with number={self.cleaned_data["number"]}'
                                                         ' already exists'))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY
