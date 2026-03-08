from functools import lru_cache
from typing import List
from django import forms
from django.db.models import Q
from django.core.exceptions import ValidationError
from rest_framework import status

from core_api.utils.access_checker import scope_for_building
from core_api.utils.presence import PresenceChecksMixin
from core_api.utils.scheme_access import ResourceAccessMixin
from models_app.models import User, Building, Scheme
from utils.fields import ModelField
from utils.services import ServiceWithResult


class UpdateBuildingService(PresenceChecksMixin, ResourceAccessMixin, ServiceWithResult):
    id = forms.IntegerField(required=True)
    current_user = ModelField(User)
    name = forms.CharField(required=False)
    coord_x = forms.FloatField(required=False)
    coord_y = forms.FloatField(required=False)

    custom_validations = ['run_presence_checks', 'number_presence', 'access_presence']
    presence_checks = [("_building", "id", "Building")]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._update_building
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def _update_building(self) -> Building:
        building = self._building
        if self.cleaned_data['name']:
            building.name = self.cleaned_data['name']
        if self.cleaned_data['coord_x']:
            building.coord_x = self.cleaned_data['coord_x']
        if self.cleaned_data['coord_y']:
            building.coord_y = self.cleaned_data['coord_y']
        building.save()
        return building

    def get_access_scope(self):
        return scope_for_building(self._building)

    @property
    @lru_cache()
    def _building(self):
        try:
            return Building.objects.select_related("scheme").get(id=self.cleaned_data['id'])
        except Building.DoesNotExist:
            return None

    @property
    def _building_list(self) -> List[Building]:
        try:
            return Building.objects.filter(scheme=self._building.scheme)
        except Building.DoesNotExist:
            return Building.objects.none()

    def number_presence(self) -> None:
        if self._building and self.cleaned_data.get('name'):
            for building in self._building_list:
                if building.name.lower() == self.cleaned_data['name'].lower():
                    self.add_error('number', ValidationError(f'Field with number={self.cleaned_data["name"]}'
                                                             ' already exists'))
                    self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY
