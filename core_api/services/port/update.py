from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import RegexValidator
from rest_framework import status
from functools import lru_cache
from typing import List
from django.db.models import Q

from utils.fields import ModelField, ListIntegerField
from utils.services import ServiceWithResult
from models_app.models import Port, User, LineType, PortMode, Access, Scheme, Building, Room, Equipment


class UpdatePortService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    line_type_id = ListIntegerField(required=False)
    mode_id = forms.IntegerField(required=False)
    mac = forms.CharField(max_length=17, validators=[RegexValidator(
        regex=r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$',
        message='Введите корректный MAC-адрес.',
        code='invalid_mac_address'
    )], required=False)

    custom_validations = ['port_presence', 'line_type_presence', 'port_mode_presence', 'access_port_presence']
    current_user = ModelField(User)

    scheme_content_type = ContentType.objects.get_for_model(Scheme)
    building_content_type = ContentType.objects.get_for_model(Building)
    room_content_type = ContentType.objects.get_for_model(Room)
    equipment_content_type = ContentType.objects.get_for_model(Equipment)

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._update_port
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def _update_port(self) -> Port:
        port = self._port
        if self.cleaned_data['line_type_id']:
            port.line_type = self._line_type
        if self.cleaned_data['mode_id']:
            port.mode = self._mode
        if self.cleaned_data['mac']:
            port.mac = self.cleaned_data['mac']
        port.save()
        return port

    @property
    @lru_cache()
    def _port(self) -> Port | None:
        try:
            return Port.objects.get(id=self.cleaned_data['id'])
        except Port.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _line_type(self) -> List[LineType]:
        try:
            return LineType.objects.filter(id__in=self.cleaned_data['line_type_id'])
        except LineType.DoesNotExist:
            return LineType.objects.none()

    @property
    @lru_cache()
    def _mode(self) -> PortMode | None:
        try:
            return PortMode.objects.get(id=self.cleaned_data['mode_id'])
        except PortMode.DoesNotExist:
            return None

    @property
    def _access_port(self) -> List[Access] | None:
        try:
            access_list = Access.objects.filter(
                Q(
                    object_type=self.scheme_content_type,
                    object_id=self._port.equipment.scheme.id,
                ) |
                Q(
                    object_type=self.equipment_content_type,
                    object_id=self._port.equipment.id
                )
            )
            if self._port.equipment.room:
                return (
                        Access.objects.filter(
                            Q(
                                object_type=self.building_content_type,
                                object_id=self._port.equipment.room.building.id
                            ) |
                            Q(
                                object_type=self.room_content_type,
                                object_id=self._port.equipment.room.id
                            ),
                        ) | access_list
                ).filter(
                    user=self.cleaned_data['current_user'],
                    role__in=['Change', 'Creator'],
                )
            if self._port.equipment.units:
                return (
                        Access.objects.filter(
                            Q(
                                object_type=self.building_content_type,
                                object_id=self._port.equipment.units[0].server_rack.building.id
                            ) |
                            Q(
                                object_type=self.room_content_type,
                                object_id=self._port.equipment.units[0].server_rack.id
                            ),
                        ) | access_list
                ).filter(
                    user=self.cleaned_data['current_user'],
                    role__in=['Change', 'Creator'],
                )
        except Access.DoesNotExist:
            return None

    def port_mode_presence(self) -> None:
        if self.cleaned_data['mode_id'] and not self._mode:
            self.add_error(
                'mode_id',
                ObjectDoesNotExist(
                    f"Port mode id={self.cleaned_data['mode_id']} not found"
                )
            )

    def line_type_presence(self) -> None:
        if self.cleaned_data['line_type_id']:
            if len(self._line_type) != len(self.cleaned_data['line_type_id']):
                self.add_error(
                    'line_type_id',
                    ObjectDoesNotExist(
                        "Line type ids not found"
                    )
                )
                self.response_status = status.HTTP_404_NOT_FOUND

    def port_presence(self) -> None:
        if not self._port:
            self.add_error('id', ObjectDoesNotExist(f"Port id ={self.cleaned_data['id']} not found"))
            self.response_status = status.HTTP_404_NOT_FOUND

    def access_port_presence(self) -> None:
        if not self._access_port:
            self.add_error(
                "front_port_list",
                PermissionError(
                    f"Access with port id={self._port.id} not found"
                )
            )
            self.response_status = status.HTTP_403_FORBIDDEN
