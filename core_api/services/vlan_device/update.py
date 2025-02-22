from typing import List

from django import forms
from functools import lru_cache

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from rest_framework import status
from rest_framework.exceptions import NotFound

from utils.services import ServiceWithResult
from utils.fields import ModelField
from models_app.models import User, Equipment, Port, VlanDevice, Scheme, Building, Room, ServerRack, Access


class UpdateVlanDeviceService(ServiceWithResult):
    current_user = ModelField(User)
    id = forms.IntegerField(required=True)
    ip = forms.GenericIPAddressField(required=False)

    custom_validations = ['equipment_presence', 'port_presence', 'vlan_device_presence', 'access_port_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._update_device
        return self

    @property
    def _update_device(self) -> VlanDevice:
        vlan_device = self._vlan_device
        if self.cleaned_data['ip']:
            vlan_device.ip = self.cleaned_data['ip']
        vlan_device.save()
        return vlan_device

    @property
    @lru_cache()
    def _equipment(self) -> Equipment | None:
        try:
            return Equipment.objects.get(id=self._vlan_device.device_id)
        except Equipment.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _port(self) -> Port | None:
        try:
            return Port.objects.get(id=self._vlan_device.device_id)
        except Port.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _vlan_device(self) -> VlanDevice | None:
        try:
            return VlanDevice.objects.get(id=self.cleaned_data['id'])
        except VlanDevice.DoesNotExist:
            return None

    @property
    def _access_port(self) -> List[Access] | None:
        scheme_content_type = ContentType.objects.get_for_model(Scheme)
        building_content_type = ContentType.objects.get_for_model(Building)
        room_content_type = ContentType.objects.get_for_model(Room)
        server_rack_content_type = ContentType.objects.get_for_model(ServerRack)
        equipment_content_type = ContentType.objects.get_for_model(Equipment)
        try:
            access_list = Access.objects.filter(
                Q(
                    object_type=scheme_content_type,
                    object_id=self._port.equipment.scheme.id,
                ) |
                Q(
                    object_type=equipment_content_type,
                    object_id=self._port.equipment.id
                )
            )
            if self._port.equipment.room:
                return (
                        Access.objects.filter(
                            Q(
                                object_type=building_content_type,
                                object_id=self._port.equipment.room.building.id
                            ) |
                            Q(
                                object_type=room_content_type,
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
                                object_type=building_content_type,
                                object_id=self._port.equipment.units.all()[0].server_rack.room.building.id
                            ) |
                            Q(
                                object_type=room_content_type,
                                object_id=self._port.equipment.units.all()[0].server_rack.room.id
                            ) |
                            Q(
                                object_type=server_rack_content_type,
                                object_id=self._port.equipment.units.all()[0].server_rack.id
                            )
                        ) | access_list
                ).filter(
                    user=self.cleaned_data['current_user'],
                    role__in=['Change', 'Creator'],
                )
        except Access.DoesNotExist:
            return None

    @property
    def _access_equipment(self) -> List[Access] | None:
        scheme_content_type = ContentType.objects.get_for_model(Scheme)
        building_content_type = ContentType.objects.get_for_model(Building)
        room_content_type = ContentType.objects.get_for_model(Room)
        server_rack_content_type = ContentType.objects.get_for_model(ServerRack)
        equipment_content_type = ContentType.objects.get_for_model(Equipment)
        try:
            access_list = Access.objects.filter(
                Q(
                    object_type=scheme_content_type,
                    object_id=self._equipment.scheme.id,
                ) |
                Q(
                    object_type=equipment_content_type,
                    object_id=self._equipment.id
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
                            ) |
                            Q(
                                object_type=server_rack_content_type,
                                object_id=self._equipment.units.all()[0].server_rack.id
                            )
                        ) | access_list
                ).filter(
                    user=self.cleaned_data['current_user'],
                    role__in=['Change', 'Creator'],
                )
        except Access.DoesNotExist:
            return None

    def equipment_presence(self) -> None:
        equipment_content_type = ContentType.objects.get_for_model(Equipment)
        if self._vlan_device.device_type == equipment_content_type and not self._equipment:
            self.add_error(
                'device_id',
                NotFound(
                    f"Device id={self.cleaned_data['device_id']} not found"
                )
            )
            self.response_status = status.HTTP_404_NOT_FOUND

    def port_presence(self) -> None:
        port_content_type = ContentType.objects.get_for_model(Port)
        if self._vlan_device.device_type == port_content_type and not self._port:
            self.add_error(
                'device_id',
                NotFound(
                    f"Device id={self.cleaned_data['device_id']} not found"
                )
            )
            self.response_status = status.HTTP_404_NOT_FOUND

    def vlan_device_presence(self) -> None:
        if self.cleaned_data['id'] == 'port' and not self._vlan_device:
            self.add_error(
                'vlan_id',
                NotFound(
                    f"Vlan id={self.cleaned_data['vlan_id']} not found"
                )
            )
            self.response_status = status.HTTP_404_NOT_FOUND

    def access_port_presence(self) -> None:
        port_content_type = ContentType.objects.get_for_model(Port)
        equipment_content_type = ContentType.objects.get_for_model(Equipment)
        if self._vlan_device.device_type == port_content_type and self._port and not self._access_port:
            self.add_error(
                "device_id",
                PermissionError(
                    f"Access with port id={self._port.id} not found"
                )
            )
            self.response_status = status.HTTP_403_FORBIDDEN

        if (self._vlan_device.device_type == equipment_content_type and self._equipment
                and not self._access_equipment):
            self.add_error(
                "device_id",
                PermissionError(
                    f"Access with equipment id={self._equipment.id} not found"
                )
            )
            self.response_status = status.HTTP_403_FORBIDDEN
