from functools import lru_cache
from typing import List

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ValidationError, PermissionDenied
from rest_framework import status

from models_app.models import Access, User
from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models import Building
from models_app.models import Scheme


class CreateBuildingService(ServiceWithResult):
    scheme_id = forms.IntegerField(required=True)
    name = forms.CharField(required=True)
    current_user = ModelField(User)

    custom_validations = ['scheme_presence', 'number_presence', 'access_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._create_building
            self.response_status = status.HTTP_201_CREATED
        return self

    @property
    def _create_building(self) -> Building:
        return Building.objects.create(scheme=self._scheme, name=self.cleaned_data['name'])

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

    @property
    def _access(self):
        scheme_content_type = ContentType.objects.get_for_model(Scheme)
        try:
            return Access.objects.get(
                user=self.cleaned_data['current_user'],
                object_type=scheme_content_type,
                object_id=self._scheme.pk,
                role__in=['Change', 'Creator']
            )
        except Access.DoesNotExist:
            return None

    def scheme_presence(self):
        if not self._scheme:
            self.add_error('scheme_id', ObjectDoesNotExist('Scheme id='
                                                           f'{self.cleaned_data["scheme_id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def number_presence(self):
        for building in self.building_list:
            if building.name.lower() == self.cleaned_data['name'].lower():
                self.add_error('number', ValidationError(f'Field with number={self.cleaned_data["name"]}'
                                                         ' already exists'))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def access_presence(self):
        if self._scheme:
            if not self._access and not self.cleaned_data['current_user'].is_superuser:
                self.add_error('current_user', PermissionDenied('Access to the schema id = '
                                                                f'{self.cleaned_data["scheme_id"]} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN
