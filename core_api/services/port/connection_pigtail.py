from django import forms
from django.core.exceptions import ObjectDoesNotExist, SuspiciousOperation
from rest_framework import status
from functools import lru_cache

from utils.services import ServiceWithResult
from models_app.models.port import Port


class ConnectionPigtailService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    connection_pigtail_id = forms.IntegerField()

    custom_validations = ['port_presence', 'port_connection_presence', 'equipment_type_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.connection_port
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def connection_port(self):
        port = self.port
        port.set_connection(self.port_connection_pigtail)
        return port

    @property
    @lru_cache()
    def port(self):
        try:
            return Port.objects.get(id=self.cleaned_data['id'])
        except Port.DoesNotExist:
            return None

    @property
    @lru_cache()
    def port_connection_pigtail(self):
        try:
            return Port.objects.get(id=self.cleaned_data['connection_pigtail_id'])
        except Port.DoesNotExist:
            return None

    def port_presence(self):
        if not self.port:
            self.add_error('id', ObjectDoesNotExist(f"Port id ={self.cleaned_data['id']} not found"))
            self.response_status = status.HTTP_404_NOT_FOUND

    def port_connection_presence(self):
        if self.port:
            if not self.port_connection_pigtail:
                self.add_error('id', ObjectDoesNotExist(f"Port connection id ="
                                                        f"{self.cleaned_data['connection_pigtail_id']} not found"))
                self.response_status = status.HTTP_404_NOT_FOUND
            else:
                if ((not self.port_connection_pigtail.connection_pigtail == self.port) and
                        not (self.port_connection_pigtail.connection_pigtail is None)):
                    self.add_error('id', SuspiciousOperation("Port connection = "
                                                             f"{self.cleaned_data['connection_pigtail_id']} "
                                                             "connected to another port"))
                    self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def equipment_type_presence(self):
        if self.port and self.port_connection_pigtail:
            if (self.port.equipment.template.type != 'Пассивное оборудование' or
                    self.port_connection_pigtail.equipment.template.type != 'Пассивное оборудование'):
                self.add_error('id', SuspiciousOperation('The equipment is not a patch panel'))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY
