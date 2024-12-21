from django import forms
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from rest_framework import status
from functools import lru_cache

from utils.services import ServiceWithResult
from utils.fields import ListIntegerField
from models_app.models.port.port_template.models import PortTemplate
from models_app.models.equipment.equipment_template.models import EquipmentTemplate
from models_app.models import TypePort, Speed, LineType


class CreatePortTemplateService(ServiceWithResult):
    name = forms.CharField(required=False)
    type_port_id = forms.IntegerField(required=False)
    modular = forms.BooleanField(required=False)
    speed_list_id = ListIntegerField(required=False)
    line_type_list_id = ListIntegerField()

    custom_validations = ['name_presence', 'type_port_presence', 'type_and_modular_presence', 'count_unit',
                          'lines_presence', 'unit_max', 'speed_presence', 'line_presence', ]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._create_port_template
            self.response_status = status.HTTP_201_CREATED
        return self

    @property
    def _create_port_template(self):
        port = PortTemplate.objects.create(
            name=self.cleaned_data['name'],
            type_port=self.type_port,
            modular=self.cleaned_data['modular'],
        )
        port.line_type.set(self._line_type)
        port.speed.set(self._speeds)
        port.save()
        return port

    @property
    def port_template(self):
        try:
            return PortTemplate.objects.all()
        except PortTemplate.DoesNotExist:
            return PortTemplate.objects.none()

    @property
    @lru_cache()
    def equipment_tmp(self):
        try:
            return EquipmentTemplate.objects.get(id=self.cleaned_data['equipment_tmp_id'])
        except EquipmentTemplate.DoesNotExist:
            return None

    @property
    @lru_cache()
    def type_port(self):
        try:
            return TypePort.objects.get(id=self.cleaned_data['type_port_id'])
        except TypePort.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _line_type(self):
        try:
            return LineType.objects.filter(id__in=self.cleaned_data['line_type_list_id'])
        except LineType.DoesNotExist:
            return LineType.objects.none()

    @property
    @lru_cache()
    def _speeds(self):
        try:
            return Speed.objects.filter(id__in=self.cleaned_data['speed_list_id'])
        except Speed.DoesNotExist:
            return Speed.objects.none()

    def name_presence(self):
        for port in self.port_template:
            if port.name == self.cleaned_data['name']:
                self.add_error('name', ValidationError(f'Field with title={self.cleaned_data["name"]}'
                                                       ' already exists'))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def type_port_presence(self):
        if self.cleaned_data['type_port_id']:
            if not self.type_port:
                self.add_error('type_port_id', ObjectDoesNotExist('Type port id='
                                                                  f'{self.cleaned_data["type_port_id"]} not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def type_and_modular_presence(self):
        if not self.type_port and (not self.cleaned_data['modular'] or self.cleaned_data['modular'] is False):
            self.add_error('modular', ValidationError('A port cannot be non-modular and cannot have a type'))
            self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def count_unit(self):
        if self.cleaned_data['unit'] and self.equipment_tmp:
            if self.equipment_tmp.number_of_units < len(self.cleaned_data['unit']):
                self.add_error('unit', ValidationError('The number of units does not match'))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def lines_presence(self):
        if self.cleaned_data['lines'] and self.equipment_tmp:
            if (len(self.cleaned_data['unit']) / self.cleaned_data['lines']) < 0.5:
                self.add_error('unit', ValidationError('Еhe number of lines per unit should not exceed 2'))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def unit_max(self):
        if self.cleaned_data['unit'] and self.equipment_tmp:
            if max(self.cleaned_data['unit']) > self.equipment_tmp.number_of_units:
                self.add_error('unit', ValidationError('The number of units is less than the available unit'))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def speed_presence(self):
        if len(self.cleaned_data['speed_list_id']) == len(self._speeds):
            self.add_error('speed_list_id', ObjectDoesNotExist(f"Speed id={self.cleaned_data['speed_list_id']} "
                                                               "not found"))

    def line_presence(self):
        if len(self.cleaned_data['line_type_list_id']) == len(self._line_type):
            self.add_error('speed_list_id', ObjectDoesNotExist(f"Speed id={self.cleaned_data['speed_list_id']} "
                                                               "not found"))
