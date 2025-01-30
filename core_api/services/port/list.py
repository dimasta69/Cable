from django import forms
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status

from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models import Port, User
from models_app.models import Equipment


class PortListService(ServiceWithResult):
    filter_equipment = forms.IntegerField(required=True)
    filter_vlan = forms.IntegerField(required=False)
    order_by = forms.CharField(required=False)
    current_user = ModelField(User)

    custom_validations = ['order_presence', 'equipment_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.filter_port_list
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def filter_port_list(self):
        port_list = self.port_list
        if self.cleaned_data['filter_vlan']:
            port_list = port_list.filter(vlan=self.cleaned_data['filter_vlan'])
        if self.cleaned_data['order_by']:
            port_list = port_list.order_by(self.cleaned_data['order_by'])
        return port_list

    @property
    def port_list(self):
        try:
            return Port.objects.filter(equipment=self.equipment).select_related('port_template__type_port')
        except Port.DoesNotExist:
            return Port.objects.none()

    @property
    def equipment(self):
        try:
            return Equipment.objects.get(id=self.cleaned_data['filter_equipment'])
        except Equipment.DoesNotExist:
            return None

    def order_presence(self):
        if self.cleaned_data.get('order_by'):
            if not self.cleaned_data.get('order_by') in ['uid', '-uid', 'connection', '-connection', 'unit', '-unit']:
                self.add_error('order_by', ObjectDoesNotExist(f"Field in model with "
                                                              f"{self.cleaned_data['order_by']} not found"))
                self.response_status = status.HTTP_404_NOT_FOUND

    def equipment_presence(self):
        if not self.equipment:
            self.add_error('filter_equipment', ObjectDoesNotExist(f"Equipment id =  "
                                                                  f"{self.cleaned_data['filter_equipment']} not found"))
            self.response_status = status.HTTP_404_NOT_FOUND
