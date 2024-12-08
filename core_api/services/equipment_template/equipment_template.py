from django import forms
from functools import lru_cache
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status

from models_app.models.equipment.equipment_template.models import EquipmentTemplate
from utils.services import ServiceWithResult


class EquipmentTemplateService(ServiceWithResult):
    id = forms.IntegerField(required=True)

    custom_validations = ['equipment_template_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.equipment_template
            self.response_status = status.HTTP_200_OK
        return self

    @property
    @lru_cache()
    def equipment_template(self):
        try:
            return EquipmentTemplate.objects.get(id=self.cleaned_data['id'])
        except EquipmentTemplate.DoesNotExist:
            return None

    def equipment_template_presence(self):
        if not self.equipment_template:
            self.add_error('id', ObjectDoesNotExist(f'Equipment template id={self.cleaned_data["id"]}'
                                                    'not found'))
            self.response_status = status.HTTP_404_NOT_FOUND
