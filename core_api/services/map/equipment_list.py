from django import forms
from functools import lru_cache

from typing import List
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied

from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models import EquipmentScheme, SchemeMap, Access, User


class EquipmentListService(ServiceWithResult):
    map_id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ['map_presence', 'access_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._equipment_list
        return self

    @property
    def _equipment_list(self) -> List[EquipmentScheme]:
        try:
            return EquipmentScheme.objects.filter(schemes=self._map)
        except EquipmentScheme.DoesNotExist:
            return EquipmentScheme.objects.none()

    @property
    @lru_cache()
    def _map(self) -> SchemeMap | None:
        try:
            return SchemeMap.objects.get(id=self.cleaned_data['map_id'])
        except SchemeMap.DoesNotExist:
            return None

    @property
    def _access(self) -> Access | None:
        try:
            return Access.objects.get(user=self.cleaned_data['current_user'], scheme=self._map.scheme)
        except Access.DoesNotExist:
            return None

    def map_presence(self) -> None:
        if not self._map:
            self.add_error(
                "map_id",
                NotFound(
                    f"Map id={self.cleaned_data['map_id']} not found"
                )
            )
            self.response_status = status.HTTP_404_NOT_FOUND

    def access_presence(self) -> None:
        if self.cleaned_data['map_id']:
            if not self._access and not self.cleaned_data['current_user'].is_superuser:
                self.add_error('current_user', PermissionDenied('Access to the map id = '
                                                                f'{self.cleaned_data["map_id"]} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN
