from django import forms
from django.db.models import Q
from functools import lru_cache
from typing import List

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ValidationError, PermissionDenied
from rest_framework import status

from models_app.models import Access, User, Unit, ServerRack, Equipment, Scheme, Building, Room
from utils.services import ServiceWithResult
from utils.fields import ListIntegerField, ModelField


class AddEquipmentUnitService(ServiceWithResult):
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
            unit_equipment.equipment = None
            unit_equipment.save()

    @property
    @lru_cache()
    def _equipment(self) -> Equipment | None:
        try:
            return Equipment.objects.get(id=self.cleaned_data['id'])
        except Equipment.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _unit_list_int(self):
        unit_list = []
        for uid in self.cleaned_data['unit_list_id']:
            try:
                unit_list.append(self._unit_list.get(id=uid))
            except Unit.DoesNotExist:
                return None
        return unit_list

    @property
    def _unit_list(self) -> List[Unit]:
        try:
            return Unit.objects.all()
        except Unit.DoesNotExist:
            return Unit.objects.none()

    @property
    def _access(self) -> Access | None:
        scheme_content_type = ContentType.objects.get_for_model(Scheme)
        building_content_type = ContentType.objects.get_for_model(Building)
        room_content_type = ContentType.objects.get_for_model(Room)
        server_rack_content_type = ContentType.objects.get_for_model(Room)
        try:
            return (Access.objects.filter(
                Q(
                    object_type=scheme_content_type,
                    object_id=self._unit_list[0].server_rack.room.building.scheme.id,
                )|
                Q(
                    object_type=building_content_type,
                    object_id=self._unit_list[0].server_rack.room.building.id,
                )|
                Q(
                    object_type=room_content_type,
                    object_id=self._unit_list[0].server_rack.room.id,
                )|
                Q(
                    object_type=server_rack_content_type,
                    object_id=self._unit_list[0].server_rack.id,
                ),
            ).filter(
                user=self.cleaned_data['current_user'],
                role__in=['Change', 'Creator'],
            ))
        except Access.DoesNotExist:
            return None

    def unit_list_presence(self) -> None:
        if not self._unit_list_int:
            self.add_error('unit_list_id', ObjectDoesNotExist('Unit list id='
                                                              f'{self.cleaned_data["unit_list_id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def equipment_presence(self) -> None:
        if not self._equipment:
            self.add_error('id', ObjectDoesNotExist(f'Equipment id={self.cleaned_data["id"]} not found'))
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

    def access_presence(self) -> None:
        if self._unit_list_int and self._equipment:
            if not self._access and not self.cleaned_data['current_user'].is_superuser:
                self.add_error('current_user', PermissionDenied('Access to the schema id = '
                                                                f'{self._unit_list_int[0].server_rack.room.building.scheme.id} '
                                                                'is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN
