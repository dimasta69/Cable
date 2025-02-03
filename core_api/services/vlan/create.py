from django import forms
from functools import lru_cache
from rest_framework.exceptions import NotFound

from utils.services import ServiceWithResult
from utils.fields import ModelField
from models_app.models import User, Equipment, Port, Vlan


class CreateVlanDeviceService(ServiceWithResult):
    current_user = ModelField(User)
    name = forms.CharField(required=True)
    vlan_id = forms.IntegerField(required=True)
    device_type = forms.CharField(required=True)
    device_id = forms.IntegerField(required=True)
    ip = forms.GenericIPAddressField(required=False)

    custom_validations = ['device_type_presence', 'equipment_presence', 'port_presence']

    @property
    def _update_device(self) -> Equipment | Port:
        if
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
    def _vlan(self) -> :
    def device_type_presence(self) -> None:
        if not self.cleaned_data['device_type'] in ['port', 'equipment']:
            self.add_error(
                "device_type",
                NotFound(
                    f"Device type={self.cleaned_data['device_type']} not found"
                )
            )

    def equipment_presence(self) -> None:
        if self.cleaned_data['device_type'] == 'equipment' and not self._equipment:
            self.add_error(
                'device_id',
                NotFound(
                    f"Device id={self.cleaned_data['device_id']} not found"
                )
            )

    def port_presence(self) -> None:
        if self.cleaned_data['device_type'] == 'port' and not self._port:
            self.add_error(
                'device_id',
                NotFound(
                    f"Device id={self.cleaned_data['device_id']} not found"
                )
            )
