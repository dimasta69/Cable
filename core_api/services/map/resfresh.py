from functools import lru_cache

from django import forms
from rest_framework import status
from typing import List

from core_api.utils.access_checker import scope_for_map
from core_api.utils.scheme_access import ResourceAccessMixin
from utils.fields import ModelField
from utils.services import ServiceWithResult
from core_api.utils.refresh_connection import refresh_connection_is_active
from models_app.models import User, SchemeMap, EquipmentScheme


class RefreshEquipmentMapService(ResourceAccessMixin, ServiceWithResult):
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

    def get_access_scope(self):
        return scope_for_map(self._map)

    @property
    @lru_cache()
    def _equipments(self) -> List[EquipmentScheme]:
        try:
            return EquipmentScheme.objects.filter(schemes=self._map)
        except EquipmentScheme.DoesNotExist:
            return EquipmentScheme.objects.none()

    @property
    @lru_cache()
    def _map(self) -> SchemeMap | None:
        try:
            return SchemeMap.objects.select_related('scheme').get(id=self.cleaned_data["id"])
        except SchemeMap.DoesNotExist:
            return None
