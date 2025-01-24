from functools import lru_cache

from django import forms
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from typing import List

from utils.fields import ModelField
from utils.services import ServiceWithResult
from core_api.utils.refresh_connection import refresh_connection_is_active
from models_app.models import User, Access, SchemeMap, EquipmentScheme


class RefreshEquipmentMapService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ["access_presence"]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._update_equipments()
        return self

    def _update_equipments(self) -> List[EquipmentScheme]:
        list(map(refresh_connection_is_active, self._equipments))
        return self._equipments

    @property
    @lru_cache()
    def _equipments(self) -> List[EquipmentScheme]:
        try:
            return EquipmentScheme.objects.filter(
                schemes=self._map,
            )
        except EquipmentScheme.DoesNotExsist:
            return EquipmentScheme.objects.none()

    @property
    @lru_cache()
    def _map(self) -> SchemeMap | None:
        try:
            return SchemeMap.objects.get(id=self.cleaned_data["id"])
        except SchemeMap.DoesNotExist:
            return None

    @property
    def _access(self) -> Access | None:
        try:
            return Access.objects.get(user=self.cleaned_data['current_user'], scheme=self._map.scheme,
                                      role__in=['Change', 'Creator'])
        except Access.DoesNotExist:
            return None

    def access_presence(self) -> None:
        if self._map:
            if not self._access and not self.cleaned_data['current_user'].is_superuser:
                self.add_error('current_user', PermissionDenied('Access to the schem id = '
                                                                f'{self._map.scheme.id} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN
