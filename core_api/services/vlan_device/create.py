from typing import List

from django import forms
from django.core.exceptions import ValidationError as DjangoValidationError
from functools import lru_cache

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from rest_framework import status
from rest_framework.exceptions import NotFound

from utils.services import ServiceWithResult
from utils.fields import ModelField
from core_api.utils.ip_mask import validate_ip_and_mask
from models_app.models import User, Equipment, Port, Vlan, VlanDevice, Scheme, Building, Room, ServerRack, Access


class CreateVlanDeviceService(ServiceWithResult):
    current_user = ModelField(User)
    vlan_id = forms.IntegerField(required=True)
    device_type = forms.CharField(required=True)
    device_id = forms.IntegerField(required=True)
    ip = forms.GenericIPAddressField(required=False)
    mask = forms.GenericIPAddressField(required=False)

    custom_validations = [
        'device_type_presence', 'equipment_presence', 'port_presence', 'vlan_presence', 'access_port_presence',
        'ip_mask_match',
    ]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._create_device
        return self

    @property
    def _device_type(self) -> ContentType:
        equipment_content_type = ContentType.objects.get_for_model(Equipment)
        port_content_type = ContentType.objects.get_for_model(Port)
        match self.cleaned_data['device_type']:
            case "equipment":
                return equipment_content_type
            case "port":
                return port_content_type
            case _:
                assert False, "Тип объкта, который не может быть"

    @property
    def _create_device(self) -> VlanDevice:
        return VlanDevice.objects.create(
            vlan=self._vlan,
            device_id=self.cleaned_data['device_id'],
            device_type=self._device_type,
            ip=self.cleaned_data.get('ip'),
            mask=self.cleaned_data.get('mask'),
        )

    @property
    @lru_cache()
    def _equipment(self) -> Equipment | None:
        try:
            return Equipment.objects.get(id=self.cleaned_data['device_id'])
        except Equipment.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _port(self) -> Port | None:
        try:
            return Port.objects.get(id=self.cleaned_data['device_id'])
        except Port.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _vlan(self) -> Vlan | None:
        try:
            return Vlan.objects.get(id=self.cleaned_data['vlan_id'])
        except Vlan.DoesNotExist:
            return None

    def ip_mask_match(self) -> None:
        try:
            validate_ip_and_mask(
                self.cleaned_data.get('ip'),
                self.cleaned_data.get('mask'),
            )
        except DjangoValidationError as e:
            self.add_error('mask', e)

    def device_type_presence(self) -> None:
        if not self.cleaned_data['device_type'] in ['port', 'equipment']:
            self.add_error(
                "device_type",
                NotFound(
                    f"Device type={self.cleaned_data['device_type']} not found"
                )
            )

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
                            ),
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
                                object_type=self.room_content_type,
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
                                object_type=server_rack_content_type,
                                object_id=self._equipment.units.all()[0].server_rack.id
                            ) |
                            Q(
                                object_type=room_content_type,
                                object_id=self._equipment.units.all()[0].server_rack.room.id
                            ),
                        ) | access_list
                ).filter(
                    user=self.cleaned_data['current_user'],
                    role__in=['Change', 'Creator'],
                )
        except Access.DoesNotExist:
            return None

    def equipment_presence(self) -> None:
        if self.cleaned_data['device_type'] == 'equipment' and not self._equipment:
            self.add_error(
                'device_id',
                NotFound(
                    f"Device id={self.cleaned_data['device_id']} not found"
                )
            )
            self.response_status = status.HTTP_404_NOT_FOUND

    def port_presence(self) -> None:
        if self.cleaned_data['device_type'] == 'port' and not self._port:
            self.add_error(
                'device_id',
                NotFound(
                    f"Device id={self.cleaned_data['device_id']} not found"
                )
            )
            self.response_status = status.HTTP_404_NOT_FOUND

    def vlan_presence(self) -> None:
        if self.cleaned_data['vlan_id'] == 'port' and not self._vlan:
            self.add_error(
                'vlan_id',
                NotFound(
                    f"Vlan id={self.cleaned_data['vlan_id']} not found"
                )
            )
            self.response_status = status.HTTP_404_NOT_FOUND

    def access_port_presence(self) -> None:
        if not self.cleaned_data["current_user"].is_superuser:
            if self.cleaned_data['device_type'] == "port" and self._port and not self._access_port:
                self.add_error(
                    "device_id",
                    PermissionError(
                        f"Access with port id={self._port.id} not found"
                    )
                )
                self.response_status = status.HTTP_403_FORBIDDEN
            if (self.cleaned_data['device_type'] == "equipment" and self._equipment and not self._access_equipment):
                self.add_error(
                    "device_id",
                    PermissionError(
                        f"Access with equipment id={self._equipment.id} not found"
                    )
                )
                self.response_status = status.HTTP_403_FORBIDDEN
