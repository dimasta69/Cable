from django import forms
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from functools import lru_cache

from utils.services import ServiceWithResult
from models_app.models.equipment_template import EquipmentTemplate
from models_app.models.manufacturer import Manufacturer


class CreateEquipmentTemplateService(ServiceWithResult):
    manufacturer_id = forms.IntegerField(required=False)
    type = forms.CharField(required=True)
    model = forms.CharField(required=True)
    number_of_units = forms.IntegerField(required=False)
    power = forms.IntegerField(required=False)

    custom_validations = ['type_presence', 'model_presence', 'manufacturer_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.create_equipment_template
            self.response_status = status.HTTP_201_CREATED
        return self

    @property
    def create_equipment_template(self):
        return EquipmentTemplate.objects.create(manufacturer=self.manufacturer,
                                                type=self.cleaned_data['type'],
                                                model=self.cleaned_data['model'],
                                                number_of_units=self.cleaned_data['number_of_units'],
                                                power=self.cleaned_data['power'])

    @property
    @lru_cache()
    def manufacturer(self):
        try:
            return Manufacturer.objects.get(id=self.cleaned_data['manufacturer_id'])
        except Manufacturer.DoesNotExist:
            return None

    @property
    def equipment_template_list(self):
        try:
            return EquipmentTemplate.objects.all()
        except EquipmentTemplate.DoesNotExist:
            return EquipmentTemplate.objects.none()

    def type_presence(self):
        if self.cleaned_data['type']:
            if not any(type_tuple[1] == self.cleaned_data['type'] for type_tuple in EquipmentTemplate.TYPE_CHOICES):
                self.add_error('type', ObjectDoesNotExist(f'Type {self.cleaned_data["type"]} not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def model_presence(self):
        for equipment in self.equipment_template_list:
            if self.cleaned_data['model'].lower() == equipment.model.lower():
                self.add_error('model', ValidationError(f'Field with model={self.cleaned_data["model"]}'
                                                        ' already exists'))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def manufacturer_presence(self):
        if self.cleaned_data['manufacturer_id']:
            if not self.manufacturer:
                self.add_error('manufacturer_id', ObjectDoesNotExist('Manufacturer  id='
                                                                     f'{self.cleaned_data["manufacturer_id"]} not '
                                                                     'found'))
                self.response_status = status.HTTP_404_NOT_FOUND
