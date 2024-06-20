from django import forms
from functools import lru_cache
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status

from utils.services import ServiceWithResult
from models_app.models.equipment import Equipment
from models_app.models.port import Port


class DeleteEquipmentService(ServiceWithResult):
    id = forms.IntegerField(required=True)

    custom_validations = ['equipment_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.delete_equipment
            self.response_status = status.HTTP_204_NO_CONTENT
        return self

    @property
    def delete_equipment(self):
        self.port_list.delete()
        self.equipment.delete()
        return None

    @property
    @lru_cache()
    def equipment(self):
        try:
            return Equipment.objects.get(id=self.cleaned_data['id'])
        except Equipment.DoesNotExist:
            return None

    @property
    @lru_cache()
    def port_list(self):
        try:
            return Port.objects.filter(equipment=self.equipment)
        except Port.DoesNotExist:
            return Port.objects.none()

    def equipment_presence(self):
        if not self.equipment:
            self.add_error('id', ObjectDoesNotExist(f'Equipment id={self.cleaned_data["id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def port_list_presence(self):
        if not self.port_list:
            self.add_error('id', ObjectDoesNotExist(f'Port list where equipment id={self.cleaned_data["id"]} '
                                                    'not found'))
            self.response_status = status.HTTP_404_NOT_FOUND
