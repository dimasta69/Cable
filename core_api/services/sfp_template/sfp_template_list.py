from django import forms
from django.core.exceptions import ObjectDoesNotExist
from functools import lru_cache
from rest_framework import status
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q

from utils.services import ServiceWithResult
from cabel.settings.rest_framework import REST_FRAMEWORK
from models_app.models.sfp_temaplate.models import SfpTemplate
from models_app.models import Manufacturer
from models_app.models import TypePort


class SfpTemplateListService(ServiceWithResult):
    page = forms.IntegerField(required=False)
    per_page = forms.IntegerField(required=False)
    order_by = forms.CharField(required=False)
    filter_manufacturer_id = forms.IntegerField(required=False)
    filter_type_port_id = forms.IntegerField(required=False)
    filter_line_type = forms.CharField(required=False)
    filter_speed = forms.IntegerField(required=False)
    search_filter = forms.CharField(required=False)

    custom_validations = ['line_type_presence', 'order_presence', 'manufacturer_presence', 'type_port_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.sfp_template_pagination
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def sfp_template_pagination(self):
        try:
            return (Paginator(self.sfp_filter_list, per_page=(self.cleaned_data['per_page'] or
                                                              REST_FRAMEWORK['PAGE_SIZE'])).
                    page(self.cleaned_data['page'] or 1))
        except EmptyPage:
            return (Paginator(self.sfp_filter_list, per_page=(self.cleaned_data['per_page'] or
                                                              REST_FRAMEWORK['PAGE_SIZE'])).page(1))

    @property
    def sfp_filter_list(self):
        sfp_template_list = self.sfp_template_list
        if self.cleaned_data['filter_manufacturer_id']:
            sfp_template_list = sfp_template_list.filter(manufacturer=self.manufacturer)
        if self.cleaned_data['filter_type_port_id']:
            sfp_template_list = sfp_template_list.filter(type_port=self.type_port)
        if self.cleaned_data['filter_line_type']:
            sfp_template_list = sfp_template_list.filter(line_type=self.cleaned_data['filter_line_type'])
        if self.cleaned_data['filter_speed']:
            sfp_template_list = sfp_template_list.filter(
                speed__contains=[self.cleaned_data['filter_speed']]
            )
        if self.cleaned_data['search_filter']:
            sfp_template_list = sfp_template_list.filter(
                Q(name__icontains=self.cleaned_data['search_filter']) |
                Q(manufacturer__name__icontains=self.cleaned_data['search_filter']))
        if self.cleaned_data['order_by']:
            sfp_template_list = sfp_template_list.order_by(self.cleaned_data['order_by'])
        return sfp_template_list

    @property
    def sfp_template_list(self):
        try:
            return SfpTemplate.objects.all()
        except SfpTemplate.DoesNotExist:
            return SfpTemplate.objects.none()

    @property
    @lru_cache()
    def manufacturer(self):
        try:
            return Manufacturer.objects.get(id=self.cleaned_data['filter_manufacturer_id'])
        except Manufacturer.DoesNotExist:
            return None

    @property
    @lru_cache()
    def type_port(self):
        try:
            return TypePort.objects.get(id=self.cleaned_data['filter_type_port_id'])
        except TypePort.DoesNotExist:
            return None

    def line_type_presence(self):
        if self.cleaned_data['filter_line_type']:
            if not any(type_tuple[1] == self.cleaned_data['filter_line_type']
                       for type_tuple in SfpTemplate.LINE_CHOICES):
                self.add_error('filter_line_type', ObjectDoesNotExist('Line type id='
                                                                      f'{self.cleaned_data["filter_line_type"]} '
                                                                      f'not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def order_presence(self):
        if self.cleaned_data['order_by']:
            if not self.cleaned_data['order_by'] in ['name', '-name']:
                self.add_error('order', ObjectDoesNotExist(f'Order {self.cleaned_data["order_by"]} is not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def manufacturer_presence(self):
        if self.cleaned_data['filter_manufacturer_id']:
            if not self.manufacturer:
                self.add_error('filter_manufacturer_id',
                               ObjectDoesNotExist(f'Manufacturer id={self.cleaned_data["filter_manufacturer_id"]} '
                                                  'not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def type_port_presence(self):
        if self.cleaned_data['filter_type_port_id']:
            if not self.type_port:
                self.add_error('filter_type_port_id', ObjectDoesNotExist('Type port id='
                                                                         f'{self.cleaned_data["filter_type_port_id"]} '
                                                                         f'not found'))
                self.response_status = status.HTTP_404_NOT_FOUND
