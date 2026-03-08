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
from models_app.models import User, Equipment, Port, Vlan, VlanDevice


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
    def _device_type(self):
        equipment_content_type = ContentType.objects.get_for_model(Equipment)
        port_content_type = ContentType.objects.get_for_model(Port)
        match self.cleaned_data['device_type']:
            case "equipment":
                return equipment_content_type
            case "port":
                return port_content_type
            case _:
                raise ValueError("Тип объекта, который не может быть")

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
            return Equipment.objects.select_related(
                'scheme', 'room', 'room__building'
            ).prefetch_related(
                'units__server_rack__room__building'
            ).get(id=self.cleaned_data['device_id'])
        except Equipment.DoesNotExist:
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
            ).get(id=self.cleaned_data['device_id'])
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
        if self.cleaned_data.get('device_type') not in ('port', 'equipment'):
            self.add_error(
                "device_type",
                NotFound(f"Device type={self.cleaned_data.get('device_type')} not found")
            )

    def equipment_presence(self) -> None:
        if self.cleaned_data.get('device_type') == 'equipment' and not self._equipment:
            self.add_error(
                'device_id',
                NotFound(f"Device id={self.cleaned_data['device_id']} not found")
            )
            self.response_status = status.HTTP_404_NOT_FOUND

    def port_presence(self) -> None:
        if self.cleaned_data.get('device_type') == 'port' and not self._port:
            self.add_error(
                'device_id',
                NotFound(f"Device id={self.cleaned_data['device_id']} not found")
            )
            self.response_status = status.HTTP_404_NOT_FOUND

    def vlan_presence(self) -> None:
        if self.cleaned_data.get('vlan_id') and not self._vlan:
            self.add_error(
                'vlan_id',
                NotFound(f"Vlan id={self.cleaned_data['vlan_id']} not found")
            )
            self.response_status = status.HTTP_404_NOT_FOUND

    def access_port_presence(self) -> None:
        user = self.cleaned_data['current_user']
        if user and getattr(user, 'is_superuser', False):
            return
        if self.cleaned_data.get('device_type') == 'port' and self._port:
            scope = scope_for_equipment(self._port.equipment)
            if not AccessChecker.has_permission(user, AccessChecker.ROLES_CHANGE, scope):
                self.add_error("device_id", PermissionError(f"Access with port id={self._port.id} not found"))
                self.response_status = status.HTTP_403_FORBIDDEN
                return
        if self.cleaned_data.get('device_type') == 'equipment' and self._equipment:
            scope = scope_for_equipment(self._equipment)
            if not AccessChecker.has_permission(user, AccessChecker.ROLES_CHANGE, scope):
                self.add_error("device_id", PermissionError(f"Access with equipment id={self._equipment.id} not found"))
                self.response_status = status.HTTP_403_FORBIDDEN
