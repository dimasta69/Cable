from functools import lru_cache

from django import forms
from django.core.exceptions import ObjectDoesNotExist, ValidationError, PermissionDenied
from rest_framework import status

from models_app.models import User, Access
from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models import Building


class UpdateBuildingService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    current_user = ModelField(User)
    name = forms.CharField(required=False)
    coord_x = forms.FloatField(required=False)
    coord_y = forms.FloatField(required=False)

    custom_validations = ['building_presence', 'number_presence', 'access_presence']

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
            building.number = self.cleaned_data['name']
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

    @property
    def access(self):
        try:
            return Access.objects.get(user=self.cleaned_data['current_user'], scheme=self.building.scheme,
                                      role__in=['Change', 'Creator'])
        except Access.DoesNotExist:
            return None

    def building_presence(self):
        if not self.building:
            self.add_error('id', ObjectDoesNotExist('Building id='
                                                    f'{self.cleaned_data["id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def number_presence(self):
        if self.building:
            for building in self.building_list:
                if building.number.lower() == self.cleaned_data['name'].lower():
                    self.add_error('number', ValidationError(f'Field with number={self.cleaned_data["name"]}'
                                                             ' already exists'))
                    self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def access_presence(self):
        if self.building:
            if not self.access and not self.cleaned_data['current_user'].is_superuser:
                self.add_error('current_user', PermissionDenied('Access to the schema id = '
                                                                f'{self.building.scheme.id} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN
