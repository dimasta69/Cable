from django import forms
from functools import lru_cache
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status

from core_api.utils.access_checker import scope_for_equipment
from core_api.utils.connection import delete_port_from_connection
from core_api.utils.scheme_access import ResourceAccessMixin
from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models import Equipment, User


class DeleteEquipmentService(ResourceAccessMixin, ServiceWithResult):
    id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ['equipment_presence', 'access_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            with transaction.atomic():
                self._disconnect_port()
                self._delete_equipment()
                self.response_status = status.HTTP_204_NO_CONTENT
        return self

    def _delete_equipment(self) -> None:
        self._equipment.delete()

    def _disconnect_port(self) -> None:
        ports = self._equipment.ports.filter(line__isnull=False)
        list(map(delete_port_from_connection, ports))

    def get_access_scope(self):
        return scope_for_equipment(self._equipment)

    @property
    @lru_cache()
    def _equipment(self) -> Equipment | None:
        try:
            return Equipment.objects.select_related(
                "scheme", "room", "room__building"
            ).prefetch_related("ports", "units__server_rack__room__building").get(
                id=self.cleaned_data['id']
            )
        except Equipment.DoesNotExist:
            return None

    def equipment_presence(self) -> None:
        if not self._equipment:
            self.add_error('id', ObjectDoesNotExist(f'Equipment id={self.cleaned_data["id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND
