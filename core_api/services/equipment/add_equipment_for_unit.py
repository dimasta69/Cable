from django import forms
from django.db.models import Q
from functools import lru_cache
from typing import List

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework import status

from core_api.utils.access_checker import scope_for_server_rack
from core_api.utils.scheme_access import ResourceAccessMixin
from models_app.models import User, Unit, ServerRack, Equipment
from utils.services import ServiceWithResult
from utils.fields import ListIntegerField, ModelField


class AddEquipmentUnitService(ResourceAccessMixin, ServiceWithResult):
    id = forms.IntegerField(required=True)
    unit_list_id = ListIntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = [
        'unit_list_presence', 'equipment_presence', 'count_unit_presence', 'power_presence', 'access_presence'
    ]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._add_equipment
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def _add_equipment(self) -> ServerRack:
        self._remove_equipment()
        for unit in self._unit_list_int:
            unit.equipment = self._equipment
            unit.save()
        return self._unit_list_int[0].server_rack

    def _remove_equipment(self) -> None:
        unit_equipment = self._unit_list.filter(equipment=self._equipment)
        if unit_equipment:
            unit_equipment.update(equipment=None)

    def get_access_scope(self):
        if self._unit_list_int:
            return scope_for_server_rack(self._unit_list_int[0].server_rack)
        return None

    @property
    @lru_cache()
    def _equipment(self) -> Equipment | None:
        try:
            return Equipment.objects.select_related('template').get(id=self.cleaned_data['id'])
        except Equipment.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _unit_list_int(self):
        unit_list = []
        for uid in self.cleaned_data['unit_list_id']:
            try:
                unit_list.append(
                    Unit.objects.select_related(
                        'server_rack', 'server_rack__room', 'server_rack__room__building'
                    ).get(id=uid)
                )
            except Unit.DoesNotExist:
                return None
        return unit_list

    @property
    def _unit_list(self) -> List[Unit]:
        try:
            return Unit.objects.all()
        except Unit.DoesNotExist:
            return Unit.objects.none()

    def unit_list_presence(self) -> None:
        if not self._unit_list_int:
            self.add_error('unit_list_id', ObjectDoesNotExist(
                'Unit list id=' f'{self.cleaned_data["unit_list_id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def equipment_presence(self) -> None:
        if not self._equipment:
            self.add_error('id', ObjectDoesNotExist(
                f'Equipment id={self.cleaned_data["id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def count_unit_presence(self) -> None:
        if self._unit_list_int and self._equipment:
            if not len(self._unit_list_int) == self._equipment.template.number_of_units:
                self.add_error('unit_list_id', ValidationError('Quantities units do not match'))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def power_presence(self) -> None:
        if self._unit_list_int and self._equipment:
            if self._unit_list_int[0].server_rack.free_power and self._equipment.template.power:
                if self._unit_list_int[0].server_rack.free_power < self._equipment.template.power:
                    self.add_error('unit_list_id', ValidationError('Not enough power'))
                    self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY
