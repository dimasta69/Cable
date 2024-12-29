from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from rest_framework import status
from functools import lru_cache

from utils.services import ServiceWithResult
from utils.fields import ListIntegerField
from models_app.models.port.port_template.models import PortTemplate
from models_app.models import Speed, LineType, TypePort
from cabel.settings.rest_framework import REST_FRAMEWORK


class PortTemplateListService(ServiceWithResult):
    page = forms.IntegerField(required=False)
    per_page = forms.IntegerField(required=False)
    order_by = forms.CharField(required=False)
    search_filter = forms.CharField(required=False)
    filter_speed = ListIntegerField(required=False)
    filter_line_type = ListIntegerField(required=False)
    filter_type_port = forms.IntegerField(required=False)
    filter_modular = forms.BooleanField(required=False)

    custom_validations = ['order_presence', 'speed_presence', 'line_type_presence', 'type_port_presence']

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
        port_list = self._port_template_list
        if self.cleaned_data['search_filter']:
            port_list = port_list.filter(
                Q(name__icontains=self.cleaned_data['search_filter'])
            )
        if self.cleaned_data['filter_speed']:
            port_list = port_list.filter(
                speed__in=self.cleaned_data['filter_speed']
            )
        if self.cleaned_data['filter_line_type']:
            port_list = port_list.filter(
                line_type__in=self.cleaned_data['filter_line_type']
            )
        if self.cleaned_data['filter_type_port']:
            port_list = port_list.filter(
                type_port=self.cleaned_data['filter_type_port']
            )
        if self.cleaned_data['filter_modular']:
            port_list = port_list.filter(
                modular=self.cleaned_data['filter_modular']
            )
        if self.cleaned_data['order_by']:
            port_list = port_list.order_by(self.cleaned_data['order_by'])
        return port_list

    @property
    def _port_template_list(self):
        try:
            return PortTemplate.objects.all()
        except PortTemplate.DoesNotExist():
            return PortTemplate.objects.none()

    @property
    @lru_cache()
    def _speeds(self) -> Speed | None:
        try:
            return Speed.objects.filter(id__in=self.cleaned_data["filter_speed"])
        except Speed.DoesNotExist:
            return Speed.objects.none()

    @property
    @lru_cache()
    def _line_type(self) -> LineType | None:
        try:
            return LineType.objects.filter(id__in=self.cleaned_data["filter_line_type"])
        except LineType.DoesNotExist:
            return LineType.objects.none()

    @property
    @lru_cache()
    def _type_port(self) -> TypePort | None:
        try:
            return TypePort.objects.filter(id__in=self.cleaned_data["filter_type_port"])
        except TypePort.DoesNotExist:
            return TypePort.objects.none()

    def order_presence(self):
        if self.cleaned_data.get('order_by'):
            if not self.cleaned_data.get('order_by') in ['name', '-name', 'count', '-count']:
                self.add_error('order_by', ObjectDoesNotExist(f"Field in model with "
                                                              f"{self.cleaned_data['order_by']} not found"))
                self.response_status = status.HTTP_404_NOT_FOUND

    def speed_presence(self):
        if self.cleaned_data['filter_speed'] and len(self.cleaned_data['filter_speed']) != len(self._speeds):
            self.add_error('filter_speed', ObjectDoesNotExist(f"Speed =  "
                                                              f"{self.cleaned_data['filter_speed']} not found"))
            self.response_status = status.HTTP_404_NOT_FOUND

    def line_type_presence(self):
        if self.cleaned_data['filter_line_type'] and len(self.cleaned_data['filter_line_type']) != len(self._line_type):
            self.add_error('filter_line_type', ObjectDoesNotExist(f"LineType =  "
                                                                  f"{self.cleaned_data['filter_line_type']} not found"))
            self.response_status = status.HTTP_404_NOT_FOUND

    def type_port_presence(self):
        if self.cleaned_data['filter_type_port'] and not self.cleaned_data['filter_type_port']:
            self.add_error('filter_type_port', ObjectDoesNotExist(f"TypePort =  "
                                                                  f"{self.cleaned_data['filter_type_port']} not found"))
            self.response_status = status.HTTP_404_NOT_FOUND
