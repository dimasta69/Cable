from functools import lru_cache
from typing import List
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist, ValidationError, PermissionDenied
from rest_framework import status

from models_app.models import User, Access
from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models import Building, Scheme


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
        # else:
        #     building.coord_x = None 
        if self.cleaned_data['coord_y']:
            building.coord_y = self.cleaned_data['coord_y']
        # else:
        #     building.coord_y = None
        building.save()
        return building

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

    @property
    def _access(self) -> Access | None:
        scheme_content_type = ContentType.objects.get_for_model(Scheme)
        building_content_type = ContentType.objects.get_for_model(Building)
        try:
            return Access.objects.filter(
                Q(object_type=scheme_content_type, object_id=self._building.scheme.id) |
                Q(object_type=building_content_type, object_id=self._building.id)
            ).filter(
                user=self.cleaned_data['current_user'],
                role__in=['Change', 'Creator'],
            )
        except Access.DoesNotExist:
            return None

    def building_presence(self) -> None:
        if not self._building:
            self.add_error('id', ObjectDoesNotExist('Building id='
                                                    f'{self.cleaned_data["id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def number_presence(self) -> None:
        if self._building:
            for building in self._building_list:
                if building.name.lower() == self.cleaned_data['name'].lower():
                    self.add_error('number', ValidationError(f'Field with number={self.cleaned_data["name"]}'
                                                             ' already exists'))
                    self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def access_presence(self) -> None:
        if self._building:
            if not self._access and not self.cleaned_data['current_user'].is_superuser:
                self.add_error('current_user', PermissionDenied('Access to the schema id = '
                                                                f'{self._building.scheme.id} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN
