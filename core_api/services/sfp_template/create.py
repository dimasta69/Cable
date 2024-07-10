from django import forms
from functools import lru_cache

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status

from utils.services import ServiceWithResult
from utils.fields import ListIntegerField
from models_app.models.manufacturer import Manufacturer
from models_app.models.type_port import TypePort
from models_app.models.sfp_template import SfpTemplate


class CreateSfpTemplateService(ServiceWithResult):
    manufacturer_id = forms.IntegerField(required=True)
    name = forms.CharField(required=False)
    type_port_id = forms.IntegerField(required=False)
    line_type = forms.CharField(required=True)
    speed = ListIntegerField()

    custom_validations = ['type_port_presence', 'manufacturer_presence', 'line_type_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.create_sfp_template
            self.response_status = status.HTTP_201_CREATED
        return self

    @property
    def create_sfp_template(self):
        return SfpTemplate.objects.create(manufacturer=self.manufacturer,
                                          name=self.cleaned_data['name'],
                                          type_port=self.type_port,
                                          line_type=self.cleaned_data['line_type'],
                                          speed=self.speed)
    def add_equipment(self):
        self.remove_equipment()
        for unit in self.unit_list_int:
            unit.equipment = self.equipment
            unit.save()
            unit.server_rack.check_free_power()
            unit.server_rack.check_free_units()
        return self.equipment
    @property
    @lru_cache()
    def manufacturer(self):
        try:
            return Manufacturer.objects.get(id=self.cleaned_data['manufacturer_id'])
        except Manufacturer.DoesNotExist:
            return None

    @property
    @lru_cache()
    def type_port(self):
        try:
            return TypePort.objects.get(id=self.cleaned_data['type_port_id'])
        except TypePort.DoesNotExist:
            return None

    def line_type_presence(self):
        if self.cleaned_data['line_type']:
            if not any(
                    type_tuple[1] == self.cleaned_data['line_type'] for type_tuple in SfpTemplate.LINE_CHOICES):
                self.add_error('filter_line_type', ObjectDoesNotExist('Line type id='
                                                                      f'{self.cleaned_data["line_type"]} '
                                                                      f'not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def manufacturer_presence(self):
        if self.cleaned_data['manufacturer_id']:
            if not self.manufacturer:
                self.add_error('filter_manufacturer_id', ObjectDoesNotExist('Manufacturer id='
                                                                            f'{self.cleaned_data["manufacturer_id"]} '
                                                                            f'not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def type_port_presence(self):
        if self.cleaned_data['type_port_id']:
            if not self.type_port:
                self.add_error('filter_type_port_id', ObjectDoesNotExist('Type port id='
                                                                         f'{self.cleaned_data["type_port_id"]} '
                                                                         f'not found'))
                self.response_status = status.HTTP_404_NOT_FOUND
