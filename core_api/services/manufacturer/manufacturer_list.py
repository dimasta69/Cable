from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from rest_framework import status

from utils.services import ServiceWithResult
from models_app.models.manufacturer import Manufacturer
from cabel.settings.rest_framework import REST_FRAMEWORK


class ManufacturerListService(ServiceWithResult):
    page = forms.IntegerField(required=False)
    per_page = forms.IntegerField(required=False)
    order_by = forms.CharField(required=False)
    search_filter = forms.CharField(required=False)

    custom_validations = ['order_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.manufacturer_pagination
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def manufacturer_pagination(self):
        try:
            return Paginator(self.filter_manufacturer_list,
                             per_page=(self.cleaned_data['per_page'] or REST_FRAMEWORK['PAGE_SIZE'])).page(
                self.cleaned_data['page'] or 1)
        except EmptyPage:
            return Paginator(self.filter_manufacturer_list,
                             per_page=(self.cleaned_data['per_page'] or REST_FRAMEWORK['PAGE_SIZE'])).page(1)

    @property
    def filter_manufacturer_list(self):
        manufacturer = self.manufacturer_list
        if self.cleaned_data['search_filter']:
            manufacturer = manufacturer.filter(
                Q(name__icontains=self.cleaned_data['search_filter'])
            )
        if self.cleaned_data['order_by']:
            manufacturer = manufacturer.order_by(self.cleaned_data['order_by'])
        return manufacturer

    @property
    def manufacturer_list(self):
        try:
            return Manufacturer.objects.all()
        except Manufacturer.DoesNotExist():
            return Manufacturer.objects.none()

    def order_presence(self):
        if self.cleaned_data.get('order_by'):
            if not self.cleaned_data.get('order_by') in ['name', '-name']:
                self.add_error('order_by', ObjectDoesNotExist(f"Field in model with "
                                                              f"{self.cleaned_data['order_by']} not found"))
                self.response_status = status.HTTP_404_NOT_FOUND
