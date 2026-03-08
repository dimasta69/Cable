from django import forms
from rest_framework import status
from django.core.exceptions import ValidationError, PermissionDenied
from functools import lru_cache

from core_api.utils.presence import PresenceChecksMixin
from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models.equipment.equipment_template.models import EquipmentTemplate
from models_app.models import Manufacturer, EquipmentTemplateType, User


class CreateEquipmentTemplateService(PresenceChecksMixin, ServiceWithResult):
    manufacturer_id = forms.IntegerField(required=False)
    type_id = forms.IntegerField(required=True)
    model = forms.CharField(required=False)
    number_of_units = forms.IntegerField(required=False)
    power = forms.IntegerField(required=False)
    current_user = ModelField(User)

    custom_validations = ['run_presence_checks', 'is_superuser']
    presence_checks = [
        ("_type", "type_id", "Type"),
        ("_manufacturer", "manufacturer_id", "Manufacturer", True),
    ]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._create_equipment_template
            self.response_status = status.HTTP_201_CREATED
        return self

    @property
    def _create_equipment_template(self) -> EquipmentTemplate:
        return EquipmentTemplate.objects.create(
            manufacturer=self._manufacturer,
            type=self._type,
            model=self.cleaned_data['model'],
            number_of_units=self.cleaned_data['number_of_units'],
            power=self.cleaned_data['power'],
        )

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

    def is_superuser(self) -> None:
        if not self.cleaned_data['current_user'].is_superuser:
            self.add_error(
                "current_user",
                PermissionDenied(
                    "User is not superuser"
                )
            )
