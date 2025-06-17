from django import forms
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist, ValidationError, PermissionDenied
from functools import lru_cache

from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models.equipment.equipment_template.models import EquipmentTemplate
from models_app.models import Manufacturer, EquipmentTemplateType, User


class CreateEquipmentTemplateService(ServiceWithResult):
    manufacturer_id = forms.IntegerField(required=False)
    type_id = forms.IntegerField(required=True)
    model = forms.CharField(required=False)
    number_of_units = forms.IntegerField(required=False)
    power = forms.IntegerField(required=False)
    current_user = ModelField(User)

    custom_validations = ['type_presence', 'manufacturer_presence', 'is_superuser']

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

    def type_presence(self) -> None:
        if self.cleaned_data['type_id']:
            if not self._type:
                self.add_error('type_id', ObjectDoesNotExist('Type  id='
                                                             f'{self.cleaned_data["type_id"]} not '
                                                             'found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def manufacturer_presence(self) -> None:
        if self.cleaned_data['manufacturer_id']:
            if not self._manufacturer:
                self.add_error('manufacturer_id', ObjectDoesNotExist('Manufacturer  id='
                                                                     f'{self.cleaned_data["manufacturer_id"]} not '
                                                                     'found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def is_superuser(self) -> None:
        if not self.cleaned_data['current_user'].is_superuser:
            self.add_error(
                "current_user",
                PermissionDenied(
                    "User is not superuser"
                )
            )
