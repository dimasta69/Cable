from django import forms
from functools import lru_cache
from django.db import transaction
from rest_framework import status

from core_api.utils.access_checker import scope_for_equipment
from core_api.utils.connection import delete_port_from_connection
from core_api.utils.presence import PresenceChecksMixin
from core_api.utils.scheme_access import ResourceAccessMixin
from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models import Equipment, User


class DeleteEquipmentService(PresenceChecksMixin, ResourceAccessMixin, ServiceWithResult):
    id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ['run_presence_checks', 'access_presence']
    presence_checks = [("_equipment", "id", "Equipment")]

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
