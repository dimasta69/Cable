from django import forms
from functools import lru_cache
from django.core.exceptions import ValidationError
from rest_framework import status
from typing import List

from rest_framework.exceptions import PermissionDenied

from core_api.utils.presence import PresenceChecksMixin
from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models.equipment.equipment_template.models import EquipmentTemplate
from models_app.models import Manufacturer, User, EquipmentTemplateType


class UpdateEquipmentTemplate(PresenceChecksMixin, ServiceWithResult):
    id = forms.IntegerField(required=True)
    manufacturer_id = forms.IntegerField(required=False)
    type_id = forms.IntegerField(required=False)
    model = forms.CharField(required=False)
    number_of_units = forms.CharField(required=False)
    power = forms.CharField(required=False)
    current_user = ModelField(User)

    custom_validations = [
        'run_presence_checks', 'model_presence', 'is_superuser',
    ]
    presence_checks = [
        ("_equipment_template", "id", "Equipment template"),
        ("_manufacturer", "manufacturer_id", "Manufacturer", True),
        ("_type", "type_id", "Type", True),
    ]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._update_equipment_template
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def _update_equipment_template(self) -> EquipmentTemplate:
        equipment_template = self._equipment_template
        if self.cleaned_data['manufacturer_id']:
            equipment_template.manufacturer = self._manufacturer
        if self.cleaned_data['type_id']:
            equipment_template.type = self._type
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
    def _equipment_template(self) -> EquipmentTemplate | None:
        try:
            return self._equipment_template_list.get(id=self.cleaned_data['id'])
        except EquipmentTemplate.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _manufacturer(self) -> Manufacturer | None:
        try:
            return Manufacturer.objects.get(id=self.cleaned_data['manufacturer_id'])
        except Manufacturer.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _type(self) -> EquipmentTemplateType | None:
        try:
            return EquipmentTemplateType.objects.get(id=self.cleaned_data['type_id'])
        except EquipmentTemplateType.DoesNotExist:
            return None

    def model_presence(self) -> None:
        if not self.cleaned_data.get('model'):
            return
        current_id = self.cleaned_data.get('id')
        for equipment in self._equipment_template_list:
            if equipment.id != current_id and self.cleaned_data['model'] == equipment.model:
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
