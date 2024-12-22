from django import forms
from rest_framework import status
from functools import lru_cache
from django.core.exceptions import ObjectDoesNotExist

from utils.errors import ValidationError
from utils.fields import ListIntegerField
from utils.services import ServiceWithResult
from models_app.models import EquipmentTemplate, PortTemplate, PortShip


class ConnectionPortShipService(ServiceWithResult):
    equipment_template_id = forms.IntegerField(required=True)
    port_template_id = forms.IntegerField(required=True)
    count = forms.IntegerField(required=True)
    unit = ListIntegerField()
    lines = forms.IntegerField(required=True)

    custom_validations = ['lines_presence', 'count_unit', 'unit_max', 'port_presence', 'equipment_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._create_port_ship
        return self

    @property
    def _create_port_ship(self):
        return PortShip.object.create(
            equipment_template=self._equipment_template,
            port_template=self._port_template,
            count=self.cleaned_data.get('count'),
            unit=self.cleaned_data.get('unit'),
            lines=self.cleaned_data.get('lines'),
        )

    @property
    @lru_cache()
    def _equipment_template(self):
        try:
            return EquipmentTemplate.objects.get(id=self.cleaned_data['equipment_template_id'])
        except EquipmentTemplate.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _port_template(self):
        try:
            return PortTemplate.objects.get(id=self.cleaned_data['port_template_id'])
        except PortTemplate.DoesNotExist:
            return None

    def lines_presence(self):
        if self.cleaned_data['lines'] and self._equipment_template:
            if (len(self.cleaned_data['unit']) / self.cleaned_data['lines']) < 0.5:
                self.add_error('unit', ValidationError('Еhe number of lines per unit should not exceed 2'))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def count_unit(self):
        if self.cleaned_data['unit'] and self._equipment_template:
            if self._equipment_template.number_of_units < len(self.cleaned_data['unit']):
                self.add_error('unit', ValidationError('The number of units does not match'))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def unit_max(self):
        if self.cleaned_data['unit'] and self._equipment_template:
            if max(self.cleaned_data['unit']) > self._equipment_template.number_of_units:
                self.add_error('unit', ValidationError('The number of units is less than the available unit'))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def port_presence(self):
        if self.cleaned_data['port_template_id'] and self._port_template is None:
            self.add_error('port_template_id', ObjectDoesNotExist(f"Port template with id="
                                                                  f"{self.cleaned_data['port_template_id']} not found"))

    def equipment_presence(self):
        if self.cleaned_data['equipment_template_id'] and self._port_template is None:
            self.add_error('equipment_template_id', ObjectDoesNotExist("Equipment template with id="
                                                                       f"{self.cleaned_data['equipment_template_id']}"
                                                                       " not found"))
