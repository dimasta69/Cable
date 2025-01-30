from functools import lru_cache

from django import forms
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.exceptions import PermissionDenied

from core_api.utils.connection import delete_port_from_connection
from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models import Equipment, Unit, Port, Scheme, Building, Room, ServerRack, Access, User


class ReleaseEquipmentService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    scheme_content_type = ContentType.objects.get_for_model(Scheme)
    building_content_type = ContentType.objects.get_for_model(Building)
    room_content_type = ContentType.objects.get_for_model(Room)
    server_rack_content_type = ContentType.objects.get_for_model(ServerRack)

    custom_validations = ["equipment_presence", "access_presence"]

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

    @property
    @lru_cache()
    def _units(self) -> Unit | None:
        try:
            return Unit.objects.filter(equipment=self._equipment)
        except Unit.DoesNotExist:
            return Unit.objects.none()

    @property
    @lru_cache()
    def _equipment(self) -> Equipment | None:
        try:
            return Equipment.objects.select_related(
                "scheme",
            ).prefetch_related(
                "buildings",
                "buildings__rooms",
                "buildings__rooms__server_racks",
            ).get(id=self.cleaned_data['id'])
        except Equipment.DoesNotExist:
            return None

    @property
    def _access(self) -> Access | None:
        try:
            return (Access.objects.filter(
                Q(
                    object_type=self.scheme_content_type,
                    object_id=self._equipment.scheme.id,
                )|
                Q(
                    object_type=self.building_content_type,
                    object_id__in=self._equipment.scheme.buildings.values("id")
                )|
                Q(
                    object_type=self.room_content_type,
                    object_id__in=self._equipment.scheme.buildings.rooms.values("id"),
                )|
                Q(
                    object_type=self.server_rack_content_type,
                    object_id__in=self._equipment.scheme.buildings.rooms.server_racks.values("id"),
                ),
            ).filter(
                user=self.cleaned_data['current_user'],
                role__in=['Change', 'Creator'],
            ))
        except Access.DoesNotExist:
            return None

    def equipment_presence(self) -> None:
        if not self._equipment:
            self.add_error('id', ObjectDoesNotExist(f"Equipment id ={self.cleaned_data['id']} not found"))
            self.response_status = status.HTTP_404_NOT_FOUND

    def access_presence(self) -> None:
        if self._equipment:
            if not self._access and not self.cleaned_data['current_user'].is_superuser:
                self.add_error('current_user', PermissionDenied('Access to the schema id = '
                                                                f'{self._equipment.scheme.id} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN
