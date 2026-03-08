from django import forms
from rest_framework import status
from functools import lru_cache

from core_api.utils.access_checker import scope_for_map
from core_api.utils.presence import PresenceChecksMixin
from core_api.utils.scheme_access import ResourceAccessMixin
from utils.services import ServiceWithResult
from utils.fields import ModelField
from core_api.utils.refresh_connection import refresh_connection_is_active
from models_app.models import User, SchemeMap, Equipment, EquipmentScheme


class AddEquipmentMapService(PresenceChecksMixin, ResourceAccessMixin, ServiceWithResult):
    map_id = forms.IntegerField(required=True)
    equipment_id = forms.IntegerField(required=True)
    current_user = ModelField(User)
    coord_x = forms.IntegerField(required=True)
    coord_y = forms.IntegerField(required=True)

    custom_validations = ['run_presence_checks', 'access_presence']
    presence_checks = [
        ("_map", "map_id", "Map"),
        ("_equipment", "equipment_id", "Equipment"),
    ]

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

    def get_access_scope(self):
        return scope_for_map(self._map)

    @property
    @lru_cache()
    def _map(self) -> SchemeMap | None:
        try:
            return SchemeMap.objects.select_related('scheme').get(id=self.cleaned_data['map_id'])
        except SchemeMap.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _equipment(self) -> Equipment | None:
        try:
            return Equipment.objects.select_related("template__type").get(id=self.cleaned_data['equipment_id'])
        except Equipment.DoesNotExist:
            return None
