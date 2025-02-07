from django import forms
from functools import lru_cache
from typing import List

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Q
from rest_framework import status

from utils.fields import ModelField
from utils.services import ServiceWithResult
from utils.fields import ListIntegerField
from models_app.models import Port, SfpTemplate, User, Access, Scheme, Building, Room, Equipment


class AddToPortSfpService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    port_list = ListIntegerField(required=True)
    current_user = ModelField(User)

    scheme_content_type = ContentType.objects.get_for_model(Scheme)
    building_content_type = ContentType.objects.get_for_model(Building)
    room_content_type = ContentType.objects.get_for_model(Room)
    equipment_content_type = ContentType.objects.get_for_model(Equipment)

    custom_validations = [
        'sfp_template_presence', 'speed_control', 'check_ports', 'access_port_presence', 'line_type_control',
    ]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self._add_sfp()
            self.response_status = status.HTTP_200_OK
        return self

    def _add_sfp(self) -> None:
        for port in self._port_list:
            port.sfp = self._sfp_template

        Port.objects.bulk_update(self._port_list, ['sfp'])

    @property
    @lru_cache()
    def _port_list(self) -> List[Port]:
        try:
            return Port.objects.filter(
                id__in=self.cleaned_data["port_list"],
                sfp__isnun=True,
                front_side__isnun=True,
                port_template__modular=True,
            ).select_related(
                "equipment",
                "equipment__template__manufacturer",
                "equipment__template__type",
                "equipment__room",
            ).prefetch_related(
                "equipment__units",
                "equipment__units__server_rack",
                "equipment__units__server_rack__room",
                "equipment__units__server_rack__room__building",
            )
        except Port.DoesNotExist:
            return Port.objects.none()

    def _access_port(self, port_id: int) -> List[Access] | None:
        try:
            access_list = Access.objects.filter(
                Q(
                    object_type=self.scheme_content_type,
                    object_id=self._port_list[port_id].equipment.scheme.id,
                ) |
                Q(
                    object_type=self.equipment_content_type,
                    object_id=self._port_list[port_id].equipment.id
                )
            )
            if self._port_list[port_id].equipment.room:
                return (
                        Access.objects.filter(
                            Q(
                                object_type=self.building_content_type,
                                object_id=self._port_list[port_id].equipment.room.building.id
                            ) |
                            Q(
                                object_type=self.room_content_type,
                                object_id=self._port_list[port_id].equipment.room.id
                            ),
                        ) | access_list
                ).filter(
                    user=self.cleaned_data['current_user'],
                    role__in=['Change', 'Creator'],
                )
            if self._port_list[port_id].equipment.units:
                return (
                        Access.objects.filter(
                            Q(
                                object_type=self.building_content_type,
                                object_id=self._port_list[port_id].equipment.units[0].server_rack.building.id
                            ) |
                            Q(
                                object_type=self.room_content_type,
                                object_id=self._port_list[port_id].equipment.units[0].server_rack.id
                            ),
                        ) | access_list
                ).filter(
                    user=self.cleaned_data['current_user'],
                    role__in=['Change', 'Creator'],
                )
        except Access.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _sfp_template(self) -> SfpTemplate | None:
        try:
            return SfpTemplate.objects.get(id=self.cleaned_data['id'])
        except SfpTemplate.DoesNotExist:
            return None

    def sfp_template_presence(self) -> None:
        if self.cleaned_data['id']:
            if not self._port_list:
                self.add_error('id', ObjectDoesNotExist('Sfp template id='
                                                        f'{self.cleaned_data["id"]} not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def check_ports(self) -> None:
        if len(self._port_list) != self.cleaned_data['port_list']:
            self.add_error(
                "port_list",
                ValidationError(
                    "Проверьте передаваемы порты на наличие подключений, находятся ли в них sfp модуль,"
                    " правильно ли вы передаете все id портов, его модульность"
                )
            )

    def speed_control(self) -> None:
        if self._port_list and self._sfp_template:
            sfp_speeds = self._sfp_template.speeds
            for port in self._port_list:
                if not set(port.speeds) & set(sfp_speeds):
                    self.add_error(
                        "id",
                        ValidationError(
                            f"Sfp with={self._sfp_template.id} не совпадают скорости с портом port_id={port.id}"
                        )
                    )

    def line_type_control(self):
        if not set(self._port_list.values("port_template__line_type")).issubset(set(self._sfp_template.line_type)):
            self.add_error(
                "id",
                ValidationError(
                    "The given ports do not correspond to sfp in line_type",
                )
            )

    def access_port_presence(self) -> None:
        if self._port_list:
            if any(port is None for port in map(self._access_port, self._port_list.iterator())):
                self.add_error(
                    "front_port_list",
                    PermissionError(
                        f"Access with port id={self._ports[0].id} not found"
                    )
                )
                self.response_status = status.HTTP_403_FORBIDDEN
