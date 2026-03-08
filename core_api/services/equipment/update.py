from django import forms
from functools import lru_cache
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status

from core_api.utils.access_checker import scope_for_equipment
from core_api.utils.scheme_access import ResourceAccessMixin
from utils.services import ServiceWithResult
from utils.fields import JsonIpField, ModelField
from models_app.models import Equipment, User


class UpdateEquipmentService(ResourceAccessMixin, ServiceWithResult):
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
        if self.cleaned_data.get('vlan_ip'):
            equipment.vlan_ip = self.cleaned_data['vlan_ip']
            equipment.save()
        return equipment

    def get_access_scope(self):
        return scope_for_equipment(self._equipment)

    @property
    @lru_cache()
    def _equipment(self) -> Equipment | None:
        try:
            return Equipment.objects.select_related(
                "scheme", "room", "room__building"
            ).prefetch_related("units__server_rack__room__building").get(
                id=self.cleaned_data['id']
            )
        except Equipment.DoesNotExist:
            return None

    def equipment_presence(self) -> None:
        if not self._equipment:
            self.add_error('id', ObjectDoesNotExist(f'Equipment id={self.cleaned_data["id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND
