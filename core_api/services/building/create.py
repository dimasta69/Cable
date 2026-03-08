from functools import lru_cache
from typing import List

from django import forms
from django.core.exceptions import ValidationError
from rest_framework import status

from core_api.utils.access_checker import scope_for_scheme
from core_api.utils.presence import PresenceChecksMixin
from core_api.utils.scheme_access import ResourceAccessMixin
from models_app.models import User, Building, Scheme
from utils.fields import ModelField
from utils.services import ServiceWithResult


class CreateBuildingService(PresenceChecksMixin, ResourceAccessMixin, ServiceWithResult):
    scheme_id = forms.IntegerField(required=True)
    name = forms.CharField(required=True)
    current_user = ModelField(User)

    custom_validations = ['run_presence_checks', 'number_presence', 'access_presence']
    presence_checks = [("_scheme", "scheme_id", "Scheme")]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._create_building
            self.response_status = status.HTTP_201_CREATED
        return self

    @property
    def _create_building(self) -> Building:
        return Building.objects.create(scheme=self._scheme, name=self.cleaned_data['name'])

    def get_access_scope(self):
        return scope_for_scheme(self._scheme)

    @property
    @lru_cache()
    def _scheme(self):
        try:
            return Scheme.objects.get(id=self.cleaned_data['scheme_id'])
        except Scheme.DoesNotExist:
            return None

    @property
    @lru_cache()
    def building_list(self) -> List[Building]:
        try:
            return Building.objects.filter(scheme=self._scheme)
        except Building.DoesNotExist:
            return Building.objects.none()

    def number_presence(self):
        for building in self.building_list:
            if building.name.lower() == self.cleaned_data['name'].lower():
                self.add_error('number', ValidationError(f'Field with number={self.cleaned_data["name"]}'
                                                         ' already exists'))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY
