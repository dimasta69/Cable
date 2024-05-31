from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from rest_framework import status

from utils.services import ServiceWithResult
from models_app.models.port_template import PortTemplate
from cabel.settings.rest_framework import REST_FRAMEWORK


class PortTemplateListService(ServiceWithResult):
    page = forms.IntegerField(required=False)
    per_page = forms.IntegerField(required=False)
    order_by = forms.CharField(required=False)
    search_filter = forms.CharField(required=False)

    custom_validations = ['order_presence']

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

    def order_presence(self):
        if self.cleaned_data.get('order_by'):
            if not self.cleaned_data.get('order_by') in ['name', '-name']:
                self.add_error('order_by', ObjectDoesNotExist(f"Field in model with "
                                                              f"{self.cleaned_data['order_by']} not found"))
                self.response_status = status.HTTP_404_NOT_FOUND
