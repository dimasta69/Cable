from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from rest_framework import status
from functools import lru_cache

from utils.services import ServiceWithResult
from models_app.models.port.port_template.models import PortTemplate
from models_app.models import Manufacturer
from models_app.models import EquipmentTemplate
from cabel.settings.rest_framework import REST_FRAMEWORK


class PortTemplateListService(ServiceWithResult):
    page = forms.IntegerField(required=False)
    per_page = forms.IntegerField(required=False)
    order_by = forms.CharField(required=False)
    search_filter = forms.CharField(required=False)
    filter_model = forms.CharField(required=False)
    filter_manufacturer = forms.IntegerField(required=False)

    custom_validations = ['order_presence', 'model_presence', 'manufacturer_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.port_template_pagination
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def port_template_pagination(self):
        try:
            return Paginator(self.filter_port_template_list,
                             per_page=(self.cleaned_data['per_page'] or REST_FRAMEWORK['PAGE_SIZE'])).page(
                self.cleaned_data['page'] or 1)
        except EmptyPage:
            return Paginator(self.filter_port_template_list,
                             per_page=(self.cleaned_data['per_page'] or REST_FRAMEWORK['PAGE_SIZE'])).page(1)

    @property
    def filter_port_template_list(self):
        port_list = self.port_template_list
        if self.cleaned_data['filter_manufacturer']:
            port_list = port_list.filter(equipment_tmp__manufacturer=self.manufacturer)
        if self.cleaned_data['filter_model']:
            port_list = port_list.filter(equipment_tmp__model=self.model)
        if self.cleaned_data['search_filter']:
            port_list = port_list.filter(
                Q(name__icontains=self.cleaned_data['search_filter'])
            )
        if self.cleaned_data['order_by']:
            port_list = port_list.order_by(self.cleaned_data['order_by'])
        return port_list

    @property
    def port_template_list(self):
        try:
            return PortTemplate.objects.all()
        except PortTemplate.DoesNotExist():
            return PortTemplate.objects.none()

    @property
    @lru_cache()
    def model(self):
        try:
            return EquipmentTemplate.objects.get(model=self.cleaned_data['filter_model']).model
        except EquipmentTemplate.DoesNotExist():
            return EquipmentTemplate.objects.none()

    @property
    @lru_cache()
    def manufacturer(self):
        try:
            return Manufacturer.objects.get(id=self.cleaned_data['filter_manufacturer'])
        except Manufacturer.DoesNotExist():
            return None

    def order_presence(self):
        if self.cleaned_data.get('order_by'):
            if not self.cleaned_data.get('order_by') in ['name', '-name', 'count', '-count']:
                self.add_error('order_by', ObjectDoesNotExist(f"Field in model with "
                                                              f"{self.cleaned_data['order_by']} not found"))
                self.response_status = status.HTTP_404_NOT_FOUND

    def model_presence(self):
        if self.cleaned_data.get('filter_model'):
            if not self.model:
                self.add_error('filter_model', ObjectDoesNotExist(f"Model =  "
                                                                  f"{self.cleaned_data['filter_model']} not found"))
                self.response_status = status.HTTP_404_NOT_FOUND

    def manufacturer_presence(self):
        if self.cleaned_data.get('filter_manufacturer'):
            if not self.manufacturer:
                self.add_error('filter_manufacturer',
                               ObjectDoesNotExist(f"Manufacturer id={self.cleaned_data['filter_manufacturer']} "
                                                  "not found"))
                self.response_status = status.HTTP_404_NOT_FOUND
