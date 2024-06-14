from django import forms
from django.core.exceptions import ObjectDoesNotExist
from functools import lru_cache
from rest_framework import status
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q

from utils.services import ServiceWithResult
from models_app.models.equipment_template import EquipmentTemplate
from models_app.models.manufacturer import Manufacturer
from cabel.settings.rest_framework import REST_FRAMEWORK


class EquipmentTemplateListService(ServiceWithResult):
    page = forms.IntegerField(required=False)
    per_page = forms.IntegerField(required=False)
    order_by = forms.CharField(required=False)
    filter_manufacturer = forms.IntegerField(required=False)
    filter_type = forms.CharField(required=False)
    search_filter = forms.CharField(required=False)

    custom_validations = ['type_presence', 'order_presence', 'manufacturer_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.equipment_template_pagination
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def equipment_template_pagination(self):
        try:
            return (Paginator(self.equipment_filter_list, per_page=(self.cleaned_data['per_page'] or
                                                                    REST_FRAMEWORK['PAGE_SIZE'])).
                    page(self.cleaned_data['page'] or 1))
        except EmptyPage:
            return (Paginator(self.equipment_filter_list, per_page=(self.cleaned_data['per_page'] or
                                                                    REST_FRAMEWORK['PAGE_SIZE'])).page(1))

    @property
    def equipment_filter_list(self):
        equipment_template_list = self.equipment_template_list
        if self.cleaned_data['filter_manufacturer']:
            equipment_template_list = equipment_template_list.filter(manufacturer=self.manufacturer)
        if self.cleaned_data['filter_type']:
            equipment_template_list = equipment_template_list.filter(type=self.filter_type)
        if self.cleaned_data['search_filter']:
            equipment_template_list = equipment_template_list.filter(
                Q(model__icontains=self.cleaned_data['search_filter']) |
                Q(manufacturer__name__icontains=self.cleaned_data['search_filter']) |
                Q(type__icontains=self.cleaned_data['search_filter']))
        if self.cleaned_data['order_by']:
            equipment_template_list = equipment_template_list.order_by(self.cleaned_data['order_by'])
        return equipment_template_list

    @property
    def equipment_template_list(self):
        try:
            return EquipmentTemplate.objects.all()
        except EquipmentTemplate.DoesNotExist:
            return EquipmentTemplate.objects.none()

    @property
    @lru_cache()
    def manufacturer(self):
        try:
            return Manufacturer.objects.get(id=self.cleaned_data['filter_manufacturer'])
        except Manufacturer.DoesNotExist:
            return None

    def type_presence(self):
        if self.cleaned_data['filter_type']:
            if not any(type_tuple[1] == self.cleaned_data['type'] for type_tuple in EquipmentTemplate.TYPE_CHOICES):
                self.add_error('filter_type', ObjectDoesNotExist('Type id='
                                                                 f'{self.cleaned_data["filter_type"]} '
                                                                 f'not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def order_presence(self):
        if self.cleaned_data['order_by']:
            if not self.cleaned_data['order_by'] in ['power', '-power', 'number_of_units', '-number_of_units',
                                                     'count_port', '-count_port', 'model', '-model']:
                self.add_error('order', ObjectDoesNotExist(f'Order {self.cleaned_data["title"]} is not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def manufacturer_presence(self):
        if self.cleaned_data['filter_manufacturer']:
            if not self.manufacturer:
                self.add_error('filter_manufacturer', ObjectDoesNotExist('Manufacturer id='
                                                                         f'{self.cleaned_data["filter_manufacturer"]} '
                                                                         f'not found'))
                self.response_status = status.HTTP_404_NOT_FOUND
