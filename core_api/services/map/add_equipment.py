from django import forms
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework import status
from functools import lru_cache

from utils.services import ServiceWithResult
from utils.fields import ModelField
from core_api.utils.refresh_connection import refresh_connection_is_active
from models_app.models import User, Access, SchemeMap, Equipment, EquipmentScheme


class AddEquipmentMapService(ServiceWithResult):
    map_id = forms.IntegerField(required=True)
    equipment_id = forms.IntegerField(required=True)
    current_user = ModelField(User)
    coord_x = forms.IntegerField(required=True)
    coord_y = forms.IntegerField(required=True)

    custom_validations = ['equipment_presence', 'map_presence', 'access_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._create_equipment_scheme
        return self

    @property
    def _create_equipment_scheme(self) -> EquipmentScheme:
        equipment_scheme = EquipmentScheme.objects.create(
                schemes=self._map,
                equipment=self._equipment,
                coord_x=self.cleaned_data['coord_x'],
                coord_y=self.cleaned_data['coord_y']
            )

        refresh_connection_is_active(equipment_scheme)

        return equipment_scheme

    @property
    @lru_cache()
    def _map(self) -> SchemeMap | None:
        try:
            return SchemeMap.objects.get(id=self.cleaned_data['map_id'])
        except SchemeMap.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _equipment(self) -> Equipment | None:
        try:
            return Equipment.objects.select_related("template__type").get(id=self.cleaned_data['equipment_id'])
        except Equipment.DoesNotExist:
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

    def map_presence(self) -> None:
        if not self._map:
            self.add_error(
                "map_id",
                NotFound(
                    f"Map id = {self.cleaned_data['map_id']} not found"
                )
            )
            self.response_status = status.HTTP_404_NOT_FOUND

    def equipment_presence(self) -> None:
        if not self._equipment:
            self.add_error(
                "equipment_id",
                NotFound(
                    f"Equipment id = {self.cleaned_data['equipment_id']} not found"
                )
            )
            self.response_status = status.HTTP_404_NOT_FOUND
