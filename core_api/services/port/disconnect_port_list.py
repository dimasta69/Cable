from django import forms
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from functools import lru_cache

from utils.services import ServiceWithResult
from utils.fields import ListIntegerField
from models_app.models.port import Port
from models_app.models.equipment import Equipment


class DisconnectPortListService(ServiceWithResult):
    port_list = ListIntegerField(required=True)
    equipment_id = forms.IntegerField(required=True)

    custom_validations = ['equipment_presence', 'port_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.disconnect_port
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def disconnect_port(self):
        for port in self.port_list_dict:
            if port.connection:
                if port.connection.connection:
                    port.connection.connection = None
                    port.connection.save()
                port.connection = None
            port.save()
        return self.port_list_int.order_by('uid')

    @property
    @lru_cache()
    def port_list_int(self):
        try:
            return Port.objects.filter(equipment=self.equipment)
        except Port.DoesNotExist:
            return Port.objects.none()

    @property
    @lru_cache()
    def port_list_dict(self):
        port_list_dict = []
        for uid in self.cleaned_data['port_list']:
            try:
                port_list_dict.append(self.port_list_int.get(id=uid))
            except Port.DoesNotExist:
                return None
        return port_list_dict

    @property
    @lru_cache()
    def equipment(self):
        try:
            return Equipment.objects.get(id=self.cleaned_data['equipment_id'])
        except Equipment.DoesNotExist:
            return None

    def equipment_presence(self):
        if not self.equipment:
            self.add_error('id', ObjectDoesNotExist(f"Equipment id ={self.cleaned_data['equipment_id']} not found"))
            self.response_status = status.HTTP_404_NOT_FOUND

    def port_presence(self):
        if not self.port_list_dict:
            self.add_error('id', ObjectDoesNotExist("Port not found"))
            self.response_status = status.HTTP_404_NOT_FOUND
