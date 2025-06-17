from django import forms
from functools import lru_cache
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework import status
from typing import List

from rest_framework.exceptions import PermissionDenied

from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models.equipment.equipment_template.models import EquipmentTemplate
from models_app.models import Manufacturer, User


class UpdateEquipmentTemplate(ServiceWithResult):
    id = forms.IntegerField(required=True)
    manufacturer_id = forms.IntegerField(required=False)
    type = forms.CharField(required=False)
    model = forms.CharField(required=False)
    number_of_units = forms.CharField(required=False)
    power = forms.CharField(required=False)
    current_user = ModelField(User)

    custom_validations = [
        'equipment_template_presence', 'manufacturer_presence', 'type_presence', 'model_presence', 'is_superuser',
    ]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._update_equipment_template
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def _update_equipment_template(self) -> EquipmentTemplate:
        equipment_template = self._equipment_template_list.get(id=self.cleaned_data['id'])
        if self.cleaned_data['manufacturer_id']:
            equipment_template.manufacturer = self._manufacturer
        if self.cleaned_data['type']:
            equipment_template.type = self.cleaned_data['type']
        if self.cleaned_data['model']:
            equipment_template.model = self.cleaned_data['model']
        if self.cleaned_data['number_of_units']:
            equipment_template.number_of_units = self.cleaned_data['number_of_units']
        if self.cleaned_data['power']:
            equipment_template.power = self.cleaned_data['power']
        equipment_template.save()
        return equipment_template

    @property
    @lru_cache()
    def _equipment_template_list(self) -> List[EquipmentTemplate]:
        try:
            return EquipmentTemplate.objects.all()
        except EquipmentTemplate.DoesNotExist:
            return EquipmentTemplate.objects.none()

    @property
    @lru_cache()
    def _manufacturer(self) -> Manufacturer | None:
        try:
            return Manufacturer.objects.get(id=self.cleaned_data['manufacturer_id'])
        except Manufacturer.DoesNotExist:
            return None

    def equipment_template_presence(self) -> None:
        if not self._equipment_template_list.get(id=self.cleaned_data['id']):
            self.add_error('id', ObjectDoesNotExist(f'Equipment template id={self.cleaned_data["id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def manufacturer_presence(self) -> None:
        if self.cleaned_data['manufacturer_id']:
            if not self._manufacturer:
                self.add_error('id', ObjectDoesNotExist(f'Manufacturer id={self.cleaned_data["manufacturer_id"]} '
                                                        'not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def type_presence(self) -> None:
        if self.cleaned_data['type']:
            if not any(type_tuple[1] == self.cleaned_data['type'] for type_tuple in EquipmentTemplate.TYPE_CHOICES):
                self.add_error('type', ObjectDoesNotExist(f'Type {self.cleaned_data["type"]} not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def model_presence(self) -> None:
        for equipment in self._equipment_template_list:
            if self.cleaned_data['model'] == equipment.model:
                self.add_error('model', ValidationError(f'Field with model={self.cleaned_data["model"]}'
                                                        ' already exists'))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def is_superuser(self) -> None:
        if not self.cleaned_data['current_user'].is_superuser:
            self.add_error(
                "current_user",
                PermissionDenied(
                    "User is not superuser"
                )
            )
