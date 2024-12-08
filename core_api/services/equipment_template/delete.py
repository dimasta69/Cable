from django import forms
from django.core.exceptions import ObjectDoesNotExist
from functools import lru_cache
from rest_framework import status

from utils.services import ServiceWithResult
from models_app.models.equipment.equipment_template.models import EquipmentTemplate


class DeleteEquipmentTemplateServcie(ServiceWithResult):
    id = forms.IntegerField(required=True)

    custom_validations = ['equipment_template_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.delete_equipment_template
            self.response_status = status.HTTP_204_NO_CONTENT
        return self

    @property
    def delete_equipment_template(self):
        self.equipment_template.delete()
        return None

    @property
    @lru_cache()
    def equipment_template(self):
        try:
            return EquipmentTemplate.objects.get(id=self.cleaned_data['id'])
        except EquipmentTemplate.DoesNotExist:
            return None

    def equipment_template_presence(self):
        if not self.equipment_template:
            self.add_error('id', ObjectDoesNotExist(f'Equipment template id={self.cleaned_data["id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND
