from django import forms
from django.core.exceptions import ValidationError as DjangoValidationError
from functools import lru_cache

from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework.exceptions import NotFound

from core_api.utils.access_checker import AccessChecker, scope_for_equipment
from core_api.utils.ip_mask import validate_ip_and_mask
from utils.services import ServiceWithResult
from utils.fields import ModelField
from models_app.models import User, Equipment, Port, VlanDevice


class UpdateVlanDeviceService(ServiceWithResult):
    current_user = ModelField(User)
    id = forms.IntegerField(required=True)
    ip = forms.GenericIPAddressField(required=False)
    mask = forms.GenericIPAddressField(required=False)

    custom_validations = [
        'equipment_presence', 'port_presence', 'vlan_device_presence', 'access_port_presence',
        'ip_mask_match',
    ]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._update_device
        return self

    @property
    def _update_device(self) -> VlanDevice:
        vlan_device = self._vlan_device
        if self.cleaned_data.get('ip'):
            vlan_device.ip = self.cleaned_data['ip']
        if 'mask' in self.cleaned_data:
            vlan_device.mask = self.cleaned_data.get('mask') or None
        vlan_device.save()
        return vlan_device

    @property
    @lru_cache()
    def _equipment(self) -> Equipment | None:
        try:
            return Equipment.objects.select_related(
                'scheme', 'room', 'room__building'
            ).prefetch_related(
                'units__server_rack__room__building'
            ).get(id=self._vlan_device.device_id)
        except (Equipment.DoesNotExist, AttributeError):
            return None

    @property
    @lru_cache()
    def _port(self) -> Port | None:
        try:
            return Port.objects.select_related(
                'equipment', 'equipment__scheme',
                'equipment__room', 'equipment__room__building',
            ).prefetch_related(
                'equipment__units__server_rack__room__building',
            ).get(id=self._vlan_device.device_id)
        except (Port.DoesNotExist, AttributeError):
            return None

    @property
    @lru_cache()
    def _vlan_device(self) -> VlanDevice | None:
        try:
            return VlanDevice.objects.select_related('device_type').get(id=self.cleaned_data['id'])
        except VlanDevice.DoesNotExist:
            return None

    def ip_mask_match(self) -> None:
        effective_ip = self.cleaned_data.get('ip') or (self._vlan_device.ip if self._vlan_device else None)
        effective_mask = (
            self.cleaned_data.get('mask') if 'mask' in self.cleaned_data
            else (self._vlan_device.mask if self._vlan_device else None)
        )
        try:
            validate_ip_and_mask(effective_ip, effective_mask)
        except DjangoValidationError as e:
            self.add_error('mask', e)

    def equipment_presence(self) -> None:
        equipment_content_type = ContentType.objects.get_for_model(Equipment)
        if (self._vlan_device and self._vlan_device.device_type_id == equipment_content_type.id
                and not self._equipment):
            self.add_error(
                'device_id',
                NotFound(f"Device id={self.cleaned_data.get('device_id', '')} not found")
            )
            self.response_status = status.HTTP_404_NOT_FOUND

    def port_presence(self) -> None:
        port_content_type = ContentType.objects.get_for_model(Port)
        if (self._vlan_device and self._vlan_device.device_type_id == port_content_type.id
                and not self._port):
            self.add_error(
                'device_id',
                NotFound(f"Device id={self.cleaned_data.get('device_id', '')} not found")
            )
            self.response_status = status.HTTP_404_NOT_FOUND

    def vlan_device_presence(self) -> None:
        if self.cleaned_data.get('id') and not self._vlan_device:
            self.add_error(
                'id',
                NotFound(f"Vlan device id={self.cleaned_data['id']} not found")
            )
            self.response_status = status.HTTP_404_NOT_FOUND

    def access_port_presence(self) -> None:
        port_content_type = ContentType.objects.get_for_model(Port)
        equipment_content_type = ContentType.objects.get_for_model(Equipment)
        user = self.cleaned_data['current_user']

        if self._vlan_device and self._vlan_device.device_type_id == port_content_type.id and self._port:
            scope = scope_for_equipment(self._port.equipment)
            if not AccessChecker.has_permission(user, AccessChecker.ROLES_CHANGE, scope):
                self.add_error("device_id", PermissionError(f"Access with port id={self._port.id} not found"))
                self.response_status = status.HTTP_403_FORBIDDEN
                return

        if self._vlan_device and self._vlan_device.device_type_id == equipment_content_type.id and self._equipment:
            scope = scope_for_equipment(self._equipment)
            if not AccessChecker.has_permission(user, AccessChecker.ROLES_CHANGE, scope):
                self.add_error("device_id", PermissionError(f"Access with equipment id={self._equipment.id} not found"))
                self.response_status = status.HTTP_403_FORBIDDEN
