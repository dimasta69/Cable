from django import forms
from functools import lru_cache
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status

from utils.services import ServiceWithResult
from models_app.models import Equipment
from models_app.models import ServerRack


class DeleteEquipmentService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    custom_validations = ['equipment_presence', 'server_rack_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self._delete_equipment()
            self.response_status = status.HTTP_204_NO_CONTENT
        return self

    def _delete_equipment(self) -> None:
        self._equipment.delete()
        return None

    @property
    @lru_cache()
    def _equipment(self) -> Equipment | None:
        try:
            return Equipment.objects.get(id=self.cleaned_data['id'])
        except Equipment.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _server_rack(self) -> ServerRack | None:
        try:
            return ServerRack.objects.get(id=self.cleaned_data['server_rack_id'])
        except ServerRack.DoesNotExist:
            return None

    def equipment_presence(self) -> None:
        if not self._equipment:
            self.add_error('id', ObjectDoesNotExist(f'Equipment id={self.cleaned_data["id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND
