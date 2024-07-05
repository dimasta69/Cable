from django import forms
from functools import lru_cache

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework import status

from utils.services import ServiceWithResult
from utils.fields import ListIntegerField
from models_app.models.equipment import Equipment
from models_app.models.unit import Unit


class AddEquipmentUnitService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    unit_list_id = ListIntegerField(required=True)

    custom_validations = ['unit_list_presence', 'equipment_presence', 'count_unit_presence', 'power_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.add_equipment
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def add_equipment(self):
        self.remove_equipment()
        for unit in self.unit_list_int:
            unit.equipment = self.equipment
            unit.save()
            unit.server_rack.check_free_power()
            unit.server_rack.check_free_units()
        return self.equipment

    def remove_equipment(self):
        unit_equipment = self.unit_list.filter(equipment=self.equipment)
        if unit_equipment:
            unit_equipment.equipment = None
            unit_equipment.save()
            unit_equipment.server_rack.check_free_power()
            unit_equipment.server_rack.check_free_units()

    @property
    @lru_cache()
    def equipment(self):
        try:
            return Equipment.objects.get(id=self.cleaned_data['id'])
        except Equipment.DoesNotExist:
            return None

    @property
    @lru_cache()
    def unit_list_int(self):
        unit_list = []
        for uid in self.cleaned_data['unit_list_id']:
            try:
                unit_list.append(self.unit_list.get(id=uid))
            except Unit.DoesNotExist:
                return None
        return unit_list

    @property
    @lru_cache()
    def unit_list(self):
        try:
            return Unit.objects.all()
        except Unit.DoesNotExist:
            return Unit.objects.none()

    def unit_list_presence(self):
        if not self.unit_list_int:
            self.add_error('unit_list_id', ObjectDoesNotExist('Unit list id='
                                                              f'{self.cleaned_data["unit_list_id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def equipment_presence(self):
        if not self.equipment:
            self.add_error('id', ObjectDoesNotExist(f'Equipment id={self.cleaned_data["id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def count_unit_presence(self):
        if self.unit_list_int and self.equipment:
            if not len(self.unit_list_int) == self.equipment.template.number_of_units:
                self.add_error('unit_list_id', ValidationError('Quantities units do not match'))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def power_presence(self):
        if self.unit_list_int and self.equipment:
            if self.unit_list_int[0].server_rack.free_power and self.equipment.template.power:
                if self.unit_list_int[0].server_rack.free_power < self.equipment.template.power:
                    self.add_error('unit_list_id', ValidationError('Not enough power'))
                    self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY
