from django import forms
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from rest_framework import status
from functools import lru_cache

from utils.services import ServiceWithResult
from utils.fields import ListIntegerField
from models_app.models.port_template import PortTemplate
from models_app.models.equipment_template import EquipmentTemplate


class CreatePortTemplateService(ServiceWithResult):
    name = forms.CharField(required=True)
    equipment_tmp_id = forms.IntegerField(required=False)
    count = forms.IntegerField(required=True)
    speed = ListIntegerField()

    custom_validations = ['name_presence', 'equipment_template_presence']

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
                                           speed=self.cleaned_data['speed'],)

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
