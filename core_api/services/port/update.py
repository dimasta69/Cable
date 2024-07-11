from django import forms
from django.core.exceptions import ObjectDoesNotExist, SuspiciousOperation
from django.core.validators import RegexValidator
from rest_framework import status
from functools import lru_cache

from utils.services import ServiceWithResult
from models_app.models.port import Port


class UpdatePortService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    line_type = forms.CharField(required=False)
    vlan_type = forms.CharField(required=False)
    vlan = forms.IntegerField(required=False)
    ip = forms.CharField(required=False, validators=[RegexValidator(
        regex='^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|'
              '[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',
        message='Введите корректный IP адрес',
        code='invalid_ip'
    )])
    mac = forms.CharField(max_length=17, validators=[RegexValidator(
        regex=r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$',
        message='Введите корректный MAC-адрес.',
        code='invalid_mac_address'
    )], required=False)
    connection_id = forms.IntegerField(required=False)

    custom_validations = ['port_presence', 'port_connection_presence', 'vlan_presence', 'line_presence', 'port_modular',
                          'port_connection_modular']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.update_port
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def update_port(self):
        port = self.port
        if self.cleaned_data['line_type']:
            port.line_type = self.cleaned_data['line_type']
        if self.cleaned_data['vlan_type']:
            port.vlan_type = self.cleaned_data['vlan_type']
        if self.cleaned_data['vlan']:
            port.vlan = self.cleaned_data['vlan']
        if self.cleaned_data['ip']:
            port.ip = self.cleaned_data['ip']
        if self.cleaned_data['mac']:
            port.mac_address = self.cleaned_data['mac']
        if self.cleaned_data['connection_id']:
            port.set_connection(self.port_connection)
        port.save()
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
    def port_connection(self):
        try:
            return Port.objects.get(id=self.cleaned_data['connection_id'])
        except Port.DoesNotExist:
            return None

    def port_presence(self):
        if not self.port:
            self.add_error('id', ObjectDoesNotExist(f"Port id ={self.cleaned_data['id']} not found"))
            self.response_status = status.HTTP_404_NOT_FOUND

    def port_connection_presence(self):
        if not self.port:
            return

        port_template = self.port.port_template
        connection_id = self.cleaned_data.get('connection_id')

        if not port_template.modular:
            if not connection_id:
                self.add_error('id', ObjectDoesNotExist(f"Port connection id={connection_id} not found"))
                self.response_status = status.HTTP_404_NOT_FOUND
                return

            if not self.port_connection:
                self.add_error('id', ObjectDoesNotExist(f"Port connection id={connection_id} not found"))
                self.response_status = status.HTTP_404_NOT_FOUND
                return

            if self.port_connection.connection != self.port and self.port_connection.connection is not None:
                self.add_error('id', SuspiciousOperation(f"Port connection {connection_id} connected to another port"))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY
                return

            if not self.port_connection.port_template.modular:
                if not set(self.port_connection.port_template.speed) & set(port_template.speed):
                    self.add_error('connection_id', SuspiciousOperation("Cannot be connected due to speed mismatch"))
                    self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY
                    return

            if self.port_connection.port_template.modular and self.port_connection.sfp:
                if not set(self.port_connection.sfp.speed) & set(port_template.speed):
                    self.add_error('connection_id', SuspiciousOperation("Cannot be connected due to speed mismatch"))
                    self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def port_modular(self):
        if self.port and self.port.port_template.modular and not self.port.sfp:
            self.add_error('id', SuspiciousOperation("SFP module required"))
            self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def port_connection_modular(self):
        if not self.port or not self.cleaned_data.get('connection_id'):
            return

        if not self.port.port_template.modular:
            return

        if not self.port_connection:
            self.add_error('id',
                           ObjectDoesNotExist(f"Port connection id ={self.cleaned_data['connection_id']} not found"))
            self.response_status = status.HTTP_404_NOT_FOUND
            return

        if self.port_connection.port_template.modular and not self.port_connection.sfp:
            self.add_error('id', SuspiciousOperation("SFP module required"))
            self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY
            return

        if self.port_connection.connection != self.port and self.port_connection.connection is not None:
            self.add_error('id', SuspiciousOperation(
                f"Port connection = {self.cleaned_data['connection_id']} connected to another port"))
            self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY
            return

        if not self.port_connection.port_template.modular:
            if not set(self.port_connection.port_template.speed) & set(self.port.sfp.speed):
                self.add_error('connection_id', SuspiciousOperation("Cannot be connected due to speed mismatch"))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY
            return

        if self.port.port_template.modular and self.port.sfp:
            if not set(self.port_connection.sfp.speed) & set(self.port.sfp.speed):
                self.add_error('connection_id', SuspiciousOperation("Cannot be connected due to speed mismatch"))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def vlan_presence(self):
        if self.cleaned_data['vlan_type']:
            if not any(type_tuple[1] == self.cleaned_data['vlan_type'] for type_tuple in Port.VLAN_CHOICES):
                self.add_error('vlan_type', ObjectDoesNotExist(f'Type {self.cleaned_data["vlan_type"]} not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def line_presence(self):
        if self.cleaned_data['line_type']:
            if not any(type_tuple[1] == self.cleaned_data['line_type'] for type_tuple in Port.LINE_CHOICES):
                self.add_error('line_type', ObjectDoesNotExist(f'Type {self.cleaned_data["line_type"]} not found'))
                self.response_status = status.HTTP_404_NOT_FOUND
