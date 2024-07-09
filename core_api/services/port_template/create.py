from django import forms
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from rest_framework import status
from functools import lru_cache

from utils.services import ServiceWithResult
from utils.fields import ListIntegerField
from models_app.models.port_template import PortTemplate
from models_app.models.equipment_template import EquipmentTemplate
from models_app.models.type_port import TypePort


class CreatePortTemplateService(ServiceWithResult):
    name = forms.CharField(required=True)
    equipment_tmp_id = forms.IntegerField(required=False)
    type_port_id = forms.IntegerField(required=False)
    count = forms.IntegerField(required=True)
    modular = forms.BooleanField(required=False)
    speed = ListIntegerField()

    custom_validations = ['name_presence', 'equipment_template_presence', 'type_port_presence',
                          'type_and_modular_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.create_port_template
            self.response_status = status.HTTP_201_CREATED
        return self

    @property
    def create_port_template(self):
        return PortTemplate.objects.create(name=self.cleaned_data['name'],
                                           count=self.cleaned_data['count'],
                                           equipment_tmp=self.equipment_tmp,
                                           speed=self.cleaned_data['speed'],
                                           type_port=self.type_port,
                                           modular=self.cleaned_data['modular'])

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

    def name_presence(self):
        for port in self.port_template:
            if port.name == self.cleaned_data['name']:
                self.add_error('name', ValidationError(f'Field with title={self.cleaned_data["name"]}'
                                                       ' already exists'))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def equipment_template_presence(self):
        if not self.equipment_tmp:
            self.add_error('equipment_tmp_id', ObjectDoesNotExist('Equipment template id='
                                                                  f'{self.cleaned_data["equipment_tmp_id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

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
