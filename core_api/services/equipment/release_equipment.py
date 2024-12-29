from functools import lru_cache

from django import forms
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status

from utils.services import ServiceWithResult
from models_app.models import Equipment, Unit


class ReleaseEquipmentService(ServiceWithResult):
    id = forms.IntegerField(required=True)

    custom_validations = ["equipment_presence"]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._update_equipment
        return self

    @property
    def _update_equipment(self):
        equipment = self._equipment
        if equipment.room:
            equipment.room = None
        if self._units:
            for unit in self._units:
                unit.equipment = None
                unit.save()
        equipment.save()
        return equipment

    @property
    @lru_cache()
    def _units(self) -> Unit | None:
        try:
            return Unit.objects.filter(equipment=self._equipment)
        except Unit.DoesNotExist:
            return Unit.objects.none()

    @property
    @lru_cache()
    def _equipment(self) -> Equipment | None:
        try:
            return Equipment.objects.get(id=self.cleaned_data['id'])
        except Equipment.DoesNotExist:
            return None

    def equipment_presence(self) -> None:
        if not self._equipment:
            self.add_error('id', ObjectDoesNotExist(f"Equipment id ={self.cleaned_data['id']} not found"))
            self.response_status = status.HTTP_404_NOT_FOUND
