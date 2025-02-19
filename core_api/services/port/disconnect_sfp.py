from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from functools import lru_cache
from typing import List
from django.db.models import Q

from utils.services import ServiceWithResult
from utils.fields import ListIntegerField, ModelField
from models_app.models import Port, User, Equipment, Access, Scheme, Building, Room, ServerRack


class DisconnectSfpService(ServiceWithResult):
    port_list = ListIntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ['port_presence', 'access_port_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self._disconnect_sfp()
            self.response_status = status.HTTP_200_OK
        return self

    def _disconnect_sfp(self) -> None:
        for port in self._ports:
            port.sfp = None
        Port.objects.bulk_update(self._ports, ['sfp'])

    @property
    @lru_cache()
    def _ports(self) -> List[Port]:
        try:
            return Port.objects.filter(
                id__in=self.cleaned_data['port_list'],
                front_side__isnull=True,
            )
        except Port.DoesNotExist:
            return Port.objects.none()

    def _access_port(self, port_id: int) -> List[Access] | None:
        scheme_content_type = ContentType.objects.get_for_model(Scheme)
        building_content_type = ContentType.objects.get_for_model(Building)
        room_content_type = ContentType.objects.get_for_model(Room)
        server_rack_content_type = ContentType.objects.get_for_model(ServerRack)
        equipment_content_type = ContentType.objects.get_for_model(Equipment)
        try:
            access_list = Access.objects.filter(
                Q(
                    object_type=scheme_content_type,
                    object_id=self._ports[port_id].equipment.scheme.id,
                ) |
                Q(
                    object_type=equipment_content_type,
                    object_id=self._ports[port_id].equipment.id
                )
            )
            if self._ports[port_id].equipment.room:
                return (
                        Access.objects.filter(
                            Q(
                                object_type=building_content_type,
                                object_id=self._ports[port_id].equipment.room.building.id
                            ) |
                            Q(
                                object_type=room_content_type,
                                object_id=self._ports[port_id].equipment.room.id
                            ),
                        ) | access_list
                ).filter(
                    user=self.cleaned_data['current_user'],
                    role__in=['Change', 'Creator'],
                )
            if self._ports[port_id].equipment.units:
                return (
                        Access.objects.filter(
                            Q(
                                object_type=building_content_type,
                                object_id=self._ports[port_id].equipment.units.all()[0].server_rack.room.building.id
                            ) |
                            Q(
                                object_type=room_content_type,
                                object_id=self._ports[port_id].equipment.units.all()[0].server_rack.room.id
                            ),
                            Q(
                                object_type=server_rack_content_type,
                                object_id=self._ports[port_id].equipment.units.all()[0].server_rack.id
                            ),
                        ) | access_list
                ).filter(
                    user=self.cleaned_data['current_user'],
                    role__in=['Change', 'Creator'],
                )
        except Access.DoesNotExist:
            return None

    def port_presence(self) -> None:
        if len(self.cleaned_data['port_list']) != len(self._ports):
            if not self._ports:
                self.add_error('port_list', ObjectDoesNotExist('Port list does not exist'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def access_port_presence(self) -> None:
        if self._ports:
            ports = list(map(self._access_port,  range(len(self._ports))))
            if any(port is None for port in ports):
                self.add_error(
                    "front_port_list",
                    PermissionError(
                        f"Access with port id={self._ports[0].id} not found"
                    )
                )
                self.response_status = status.HTTP_403_FORBIDDEN
