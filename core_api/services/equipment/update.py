from django import forms
from functools import lru_cache
from typing import List

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from rest_framework import status

from utils.services import ServiceWithResult
from utils.fields import JsonIpField, ModelField
from models_app.models import Equipment, Access, Scheme, Building, Room, ServerRack, User


class UpdateEquipmentService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    vlan_ip = JsonIpField(required=False)
    current_user = ModelField(User)

    custom_validations = ['equipment_presence', 'access_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._update_equipment
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def _update_equipment(self) -> Equipment:
        equipment = self._equipment
        if self.cleaned_data['vlan_ip']:
            equipment.vlan_ip = self.cleaned_data['vlan_ip']
            equipment.save()
        return equipment

    @property
    @lru_cache()
    def _equipment(self) -> Equipment | None:
        try:
            return Equipment.objects.select_related(
                "scheme",
            ).get(id=self.cleaned_data['id'])
        except Equipment.DoesNotExist:
            return None

    def _access(self, port_id: int) -> List[Access] | None:
        scheme_content_type = ContentType.objects.get_for_model(Scheme)
        building_content_type = ContentType.objects.get_for_model(Building)
        room_content_type = ContentType.objects.get_for_model(Room)
        server_rack_content_type = ContentType.objects.get_for_model(ServerRack)

        try:
            access_list = Access.objects.filter(
                Q(
                    object_type=scheme_content_type,
                    object_id=self._equipment.scheme.id,
                )
            )
            if self._equipment.room:
                return (
                        Access.objects.filter(
                            Q(
                                object_type=building_content_type,
                                object_id=self._equipment.room.building.id
                            ) |
                            Q(
                                object_type=room_content_type,
                                object_id=self._equipment.room.id
                            ),
                        ) | access_list
                ).filter(
                    user=self.cleaned_data['current_user'],
                    role__in=['Change', 'Creator'],
                )
            if self._equipment.units:
                return (
                        Access.objects.filter(
                            Q(
                                object_type=building_content_type,
                                object_id=self._equipment.units.all()[0].server_rack.room.building.id
                            ) |
                            Q(
                                object_type=room_content_type,
                                object_id=self._equipment.units.all()[0].server_rack.room.id
                            ),
                            Q(
                                object_type=server_rack_content_type,
                                object_id=self._equipment.units.all()[0].server_rack.id
                            ),
                        ) | access_list
                ).filter(
                    user=self.cleaned_data['current_user'],
                    role__in=['Change', 'Creator'],
                )
        except Access.DoesNotExist:
            return None

    def equipment_presence(self) -> None:
        if not self._equipment:
            self.add_error('id', ObjectDoesNotExist(f'Equipment id={self.cleaned_data["id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def access_presence(self) -> None:
        if self._equipment:
            if not self._access and not self.cleaned_data['current_user'].is_superuser:
                self.add_error('current_user', PermissionDenied('Access to the schema id = '
                                                                f'{self._equipment.scheme.id} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN
