from django import forms
from django.core.exceptions import ObjectDoesNotExist
from functools import lru_cache

from rest_framework import status

from utils.services import ServiceWithResult
from models_app.models import Equipment


class EquipmentService(ServiceWithResult):
    id = forms.IntegerField(required=True)

    custom_validations = ['equipment_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.equipment
            self.response_status = status.HTTP_200_OK
        return self

    @property
    @lru_cache()
    def equipment(self):
        try:
            return Equipment.objects.get(id=self.cleaned_data['id'])
        except Equipment.DoesNotExist:
            return None

    def equipment_presence(self):
        if not self.equipment:
            self.add_error('id', ObjectDoesNotExist(f'Equipment id={self.cleaned_data["id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND
