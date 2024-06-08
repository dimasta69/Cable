from django import forms
from rest_framework import status
from rest_framework.fields import ModelField
from django.core.exceptions import ObjectDoesNotExist

from utils.services import ServiceWithResult
from models_app.models.equipment_template import EquipmentTemplate
from models_app.models.manufacturer import Manufacturer


class CreateEquipmentTemplateService(ServiceWithResult):
    manufacturer_id = forms.IntegerField(required=False)
    type = forms.CharField(required=True)
    model = forms.CharField(required=True)
    number_of_units = forms.IntegerField(required=False)
    power = forms.IntegerField(required=False)

    custom_validations = ['type_presence', ]

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
    def manufacturer(self):
        try:
            return Manufacturer.objects.get(id=self.cleaned_data['manufacturer_id'])
        except Manufacturer.DoesNotExist:
            return None

    def type_presence(self):
        if self.cleaned_data['type']:
            if not any(type_tuple[1] == self.cleaned_data['type'] for type_tuple in EquipmentTemplate.TYPE_CHOICES):
                self.add_error('type', ObjectDoesNotExist(f'Type {self.cleaned_data["type"]} not found'))
                self.response_status = status.HTTP_404_NOT_FOUND
