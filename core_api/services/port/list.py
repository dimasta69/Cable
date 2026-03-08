from django import forms
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from functools import lru_cache

from core_api.utils.access_checker import AccessChecker, scope_for_equipment
from core_api.utils.presence import PresenceChecksMixin
from core_api.utils.scheme_access import ResourceAccessMixin
from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models import Port, User, Equipment


class PortListService(PresenceChecksMixin, ResourceAccessMixin, ServiceWithResult):
    filter_equipment = forms.IntegerField(required=True)
    filter_vlan = forms.IntegerField(required=False)
    order_by = forms.CharField(required=False)
    current_user = ModelField(User)

    access_required_roles = AccessChecker.ROLES_READ
    custom_validations = ['run_presence_checks', 'order_presence', 'access_presence']
    presence_checks = [("equipment", "filter_equipment", "Equipment")]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.filter_port_list
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def filter_port_list(self):
        port_list = self.port_list
        if self.cleaned_data.get('filter_vlan'):
            port_list = port_list.filter(vlan=self.cleaned_data['filter_vlan'])
        if self.cleaned_data.get('order_by'):
            port_list = port_list.order_by(self.cleaned_data['order_by'])
        return port_list

    @property
    def port_list(self):
        try:
            return Port.objects.filter(equipment=self.equipment).select_related('port_template__type_port')
        except Port.DoesNotExist:
            return Port.objects.none()

    def get_access_scope(self):
        return scope_for_equipment(self.equipment)

    @property
    @lru_cache()
    def equipment(self):
        try:
            return Equipment.objects.select_related(
                'scheme', 'room', 'room__building'
            ).prefetch_related(
                'units__server_rack__room__building'
            ).get(id=self.cleaned_data['filter_equipment'])
        except Equipment.DoesNotExist:
            return None

    def order_presence(self):
        if self.cleaned_data.get('order_by'):
            if self.cleaned_data.get('order_by') not in [
                'uid', '-uid', 'connection', '-connection', 'unit', '-unit'
            ]:
                self.add_error('order_by', ObjectDoesNotExist(
                    f"Field in model with {self.cleaned_data['order_by']} not found"))
                self.response_status = status.HTTP_404_NOT_FOUND

