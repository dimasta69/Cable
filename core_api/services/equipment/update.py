from django import forms
from functools import lru_cache
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status

from utils.services import ServiceWithResult
from utils.fields import JsonIpField
from models_app.models import Equipment


class UpdateEquipmentService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    vlan_ip = JsonIpField(required=False)

    custom_validations = ['equipment_presence']

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
            return Equipment.objects.get(id=self.cleaned_data['id'])
        except Equipment.DoesNotExist:
            return None

    def equipment_presence(self) -> None:
        if not self._equipment:
            self.add_error('id', ObjectDoesNotExist(f'Equipment id={self.cleaned_data["id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND
