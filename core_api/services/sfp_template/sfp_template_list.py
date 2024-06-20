from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from functools import lru_cache

from rest_framework import status

from cabel.settings import REST_FRAMEWORK
from utils.services import ServiceWithResult
from models_app.models.sfp_template import SfpTemplate
from models_app.models.manufacturer import Manufacturer


class SfpTemplateListService(ServiceWithResult):
    page = forms.IntegerField(required=False)
    per_page = forms.IntegerField(required=False)
    filter_manufacturer = forms.IntegerField(required=False)
    search_filter = forms.CharField(required=False)
    order_by = forms.CharField(required=False)

    custom_validations = ['manufacturer_presence', 'order_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.sfp_template_pagination
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def sfp_template_pagination(self):
        try:
            return (Paginator(self.sfp_template_filter_list, per_page=(self.cleaned_data['per_page'] or
                                                                    REST_FRAMEWORK['PAGE_SIZE'])).
                    page(self.cleaned_data['page'] or 1))
        except EmptyPage:
            return (Paginator(self.sfp_template_filter_list, per_page=(self.cleaned_data['per_page'] or
                                                                    REST_FRAMEWORK['PAGE_SIZE'])).page(1))

    @property
    def sfp_template_filter_list(self):
        sfp_template_list = self.sfp_template_list
        if self.cleaned_data['filter_manufacturer']:
            sfp_template_list = sfp_template_list.filter(manufacturer__id=self.cleaned_data['filter_manufacturer'])
        if self.cleaned_data['order_by']:
            sfp_template_list = sfp_template_list.order_by(self.cleaned_data['order_by'])
        if self.cleaned_data['search_filter']:
            sfp_template_list = sfp_template_list.filter(
                Q(manufacturer__name__icontains=self.cleaned_data['search_filter']) |
                Q(speed__icontains=self.cleaned_data['search_filter'])
            )
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
            return Manufacturer.objects.get(id=self.cleaned_data['filter_manufacturer'])
        except Manufacturer.DoesNotExist:
            return None

    def manufacturer_presence(self):
        if self.cleaned_data['filter_manufacturer']:
            if not self.manufacturer:
                self.add_error('filter_manufacturer', ObjectDoesNotExist('Manufacturer id='
                                                                         f'{self.cleaned_data["filter_manufacturer"]} '
                                                                         f'not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def order_presence(self):
        if self.cleaned_data['order_by']:
            if not self.cleaned_data['order_by'] in ['speed', '-speed', 'name', '-name']:
                self.add_error('order', ObjectDoesNotExist(f'Order {self.cleaned_data["order_by"]} is not found'))
                self.response_status = status.HTTP_404_NOT_FOUND
