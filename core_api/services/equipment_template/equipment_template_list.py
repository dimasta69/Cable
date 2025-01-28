from django import forms
from django.core.exceptions import ObjectDoesNotExist
from functools import lru_cache
from rest_framework import status
from django.db.models import Q
from typing import List

from utils.services import ServiceWithResult
from models_app.models.equipment.equipment_template.models import EquipmentTemplate
from models_app.models import EquipmentTemplateType
from models_app.models import Manufacturer


class EquipmentTemplateListService(ServiceWithResult):
    filter_manufacturer_id = forms.IntegerField(required=False)
    filter_type_id = forms.IntegerField(required=False)
    search_filter = forms.CharField(required=False)
    order_by = forms.CharField(required=False)

    custom_validations = ['type_presence', 'order_presence', 'manufacturer_presence', 'type_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._equipment_filter_list
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def _equipment_filter_list(self) -> List[EquipmentTemplate]:
        equipment_template_list = self._equipment_template_list
        if self.cleaned_data['filter_manufacturer_id']:
            equipment_template_list = equipment_template_list.filter(manufacturer=self._manufacturer)
        if self.cleaned_data['filter_type_id']:
            equipment_template_list = equipment_template_list.filter(type=self._type)
        if self.cleaned_data['search_filter']:
            equipment_template_list = equipment_template_list.filter(
                Q(model__icontains=self.cleaned_data['search_filter']) |
                Q(manufacturer__name__icontains=self.cleaned_data['search_filter']) |
                Q(type__name__icontains=self.cleaned_data['search_filter']))
        if self.cleaned_data['order_by']:
            equipment_template_list = equipment_template_list.order_by(self.cleaned_data['order_by'])
        return equipment_template_list

    @property
    def _equipment_template_list(self) -> List[EquipmentTemplate]:
        try:
            return EquipmentTemplate.objects.all().select_related('manufacturer')
        except EquipmentTemplate.DoesNotExist:
            return EquipmentTemplate.objects.none()

    @property
    @lru_cache()
    def _manufacturer(self) -> Manufacturer | None:
        try:
            return Manufacturer.objects.get(id=self.cleaned_data['filter_manufacturer_id'])
        except Manufacturer.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _type(self) -> EquipmentTemplate | None:
        try:
            return EquipmentTemplateType.objects.get(id=self.cleaned_data['filter_type_id'])
        except EquipmentTemplateType.DoesNotExist:
            return None

    def type_presence(self) -> None:
        if self.cleaned_data['filter_type_id'] and self._type is None:
            self.add_error('filter_type', ObjectDoesNotExist('Type id='
                                                             f'{self.cleaned_data["filter_type_id"]} '
                                                             f'not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def order_presence(self) -> None:
        if self.cleaned_data['order_by']:
            if not self.cleaned_data['order_by'] in ['power', '-power', 'number_of_units', '-number_of_units',
                                                     'count_port', '-count_port', 'model', '-model']:
                self.add_error('order', ObjectDoesNotExist(f'Order {self.cleaned_data["order_by"]} is not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def manufacturer_presence(self) -> None:
        if self.cleaned_data['filter_manufacturer_id'] and not self._manufacturer:
            self.add_error('filter_manufacturer', ObjectDoesNotExist('Manufacturer id='
                                                                     f'{self.cleaned_data["filter_manufacturer_id"]} '
                                                                     f'not found'))
            self.response_status = status.HTTP_404_NOT_FOUND
