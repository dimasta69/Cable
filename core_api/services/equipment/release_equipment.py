from functools import lru_cache

from django import forms
from rest_framework import status

from core_api.utils.access_checker import scope_for_equipment
from core_api.utils.connection import delete_port_from_connection
from core_api.utils.presence import PresenceChecksMixin
from core_api.utils.scheme_access import ResourceAccessMixin
from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models import Equipment, Unit, Port, User


class ReleaseEquipmentService(PresenceChecksMixin, ResourceAccessMixin, ServiceWithResult):
    id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ["run_presence_checks", "access_presence"]
    presence_checks = [("_equipment", "id", "Equipment")]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self._update_connection_port()
            self.result = self._update_equipment
        return self

    def _update_connection_port(self) -> None:
        for port in Port.objects.filter(equipment=self._equipment, line__isnull=False):
            delete_port_from_connection(port)

    @property
    def _update_equipment(self) -> Equipment:
        equipment = self._equipment
        if equipment.room:
            equipment.room = None
        if self._units:
            for unit in self._units:
                unit.equipment = None
                unit.save()
        equipment.save()
        return equipment

    def get_access_scope(self):
        return scope_for_equipment(self._equipment)

    @property
    @lru_cache()
    def _units(self):
        try:
            return Unit.objects.filter(equipment=self._equipment).select_related(
                'server_rack', 'server_rack__room', 'server_rack__room__building'
            )
        except Unit.DoesNotExist:
            return Unit.objects.none()

    @property
    @lru_cache()
    def _equipment(self) -> Equipment | None:
        try:
            return Equipment.objects.select_related(
                "scheme", "room", "room__building"
            ).prefetch_related("units__server_rack__room__building").get(
                id=self.cleaned_data['id']
            )
        except Equipment.DoesNotExist:
            return None
